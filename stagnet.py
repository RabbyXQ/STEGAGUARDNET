import math
import hashlib
import torch
import torch.nn as nn
from androguard.core.bytecodes.apk import APK
from androguard.misc import AnalyzeAPK
from lxml.etree import tostring

# Utility: Calculate Entropy
def calculate_entropy(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    byte_freq = [0] * 256
    for byte in data:
        byte_freq[byte] += 1
    entropy = 0
    for freq in byte_freq:
        if freq > 0:
            prob = freq / len(data)
            entropy -= prob * math.log2(prob)
    return entropy


# 1. Certificate Analysis
def analyze_certificates(apk):
    try:
        signatures = apk.get_signature_names()
        if signatures:
            print(f"Signature Names: {signatures}")
        for cert in apk.get_certificates():
            cert_bytes = bytes(cert)
            cert_hash = hashlib.sha256(cert_bytes).hexdigest()
            cert_entropy = calculate_entropy(cert_bytes)
            print(f"Certificate Hash: {cert_hash}, Entropy: {cert_entropy}")
            if cert_entropy > 7.5:
                return 1  # Obfuscation or steganography detected in certificate
        return 0
    except Exception as e:
        print(f"Error analyzing certificates: {e}")
        return 0


# 2. Manifest Analysis
def analyze_manifest(apk):
    try:
        manifest_axml = apk.get_android_manifest_axml()
        if manifest_axml is not None:
            manifest_str = tostring(manifest_axml, encoding="utf-8").decode("utf-8")
            manifest_entropy = calculate_entropy(manifest_str)
            if manifest_entropy > 7.5:
                return 1  # Obfuscation or steganography detected in manifest
        return 0
    except Exception as e:
        print(f"Error analyzing manifest: {e}")
        return 0


# 3. DEX Analysis
def analyze_dex(apk, dvm):
    try:
        dex_files = apk.get_dex()
        if not dex_files:
            print("No valid DEX files found.")
            return 0
        for dex in dex_files:
            dex_entropy = calculate_entropy(dex)
            if dex_entropy > 7.5:
                return 1  # Obfuscation or steganography detected in DEX files
        return 0
    except Exception as e:
        print(f"Error analyzing DEX files: {e}")
        return 0


# 4. Analyze Methods for Obfuscation
def analyze_methods(dvm):
    try:
        if not dvm.get_methods():
            print("DVM does not have methods to analyze.")
            return 0
        for method in dvm.get_methods():
            code = method.get_code()
            if code:
                bytecode = code.get_bc().get_raw()
                method_entropy = calculate_entropy(bytecode)
                if method_entropy > 7.5:
                    return 1  # Obfuscation detected in method
        return 0
    except Exception as e:
        print(f"Error analyzing methods: {e}")
        return 0


# Adjusted StagNet Model for 1D Data
class StagNet(nn.Module):
    def __init__(self):
        super(StagNet, self).__init__()
        self.fc1 = nn.Linear(4, 128)  # Input size matches the entropy features
        self.rnn = nn.RNN(input_size=128, hidden_size=64, num_layers=1, batch_first=True)
        self.gru = nn.GRU(input_size=64, hidden_size=32, num_layers=1, batch_first=True)
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))  # First fully connected layer
        x, _ = self.rnn(x)
        x, _ = self.gru(x)
        x = self.fc2(x[:, -1, :])  # Use the last output from the GRU
        return torch.sigmoid(x)  # Output as a probability


# Main function to analyze APK and use StagNet for prediction
def analyze_apk_and_predict(apk_path):
    print(f"Analyzing APK: {apk_path}")
    try:
        apk, dvm, analysis = AnalyzeAPK(apk_path)
    except Exception as e:
        print(f"Error analyzing APK file: {e}")
        return

    # Entropy-based analysis
    cert_result = analyze_certificates(apk)
    manifest_result = analyze_manifest(apk)
    dex_result = analyze_dex(apk, dvm)
    method_result = analyze_methods(dvm)

    # Combining entropy analysis results (0 for no issues, 1 for issues detected)
    entropy_features = [cert_result, manifest_result, dex_result, method_result]

    # Convert to a tensor for StagNet
    input_tensor = torch.tensor(entropy_features, dtype=torch.float32).view(1, 1, 4)  # Reshaped for the model

    # Load the model and make prediction
    model = StagNet()
    model.eval()  # Set model to evaluation mode
    with torch.no_grad():
        prediction = model(input_tensor)

    print(f"Prediction: {prediction.item()}")
    if prediction.item() > 0.5:
        print("Malicious APK: Obfuscation or steganography detected!")
    else:
        print("APK appears safe.")


if __name__ == "__main__":
    apk_path = "b.apk"  # Replace with the actual path to your APK
    analyze_apk_and_predict(apk_path)
