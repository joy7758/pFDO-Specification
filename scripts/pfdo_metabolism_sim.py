"""
pFDO Metabolism & MIP Protocol Simulator (v1.0)
Architecture: Carbon-Silicon Synergy
Author: Zhangbin (FDO Architect)
"""

import math

class PFDOObject:
    def __init__(self, identifier, physical_epitope, energy_threshold=1.0):
        self.id = identifier
        self.epitope = physical_epitope  # Pre-registered physical fingerprint
        self.energy_threshold = energy_threshold  # Thermodynamic constraint
        self.state = "DORMANT"

    def verify_mip(self, current_fingerprint, rssi):
        """MIP Protocol: Physical Proximity = Security"""
        # Calculate Euclidean distance between signals
        distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(current_fingerprint, self.epitope)]))
        
        # Security Thresholds
        EPSILON = 0.05 
        RSSI_THRESHOLD = -60 # dBm
        
        return distance < EPSILON and rssi > RSSI_THRESHOLD

    def update_state(self, new_data, harvested_energy):
        """Thermodynamic Logic Gate: Metabolism check"""
        # Landauer's Principle: Any state change consumes energy
        # Simplified: Energy required = log2(Information Entropy Change)
        required_energy = self.energy_threshold
        
        if harvested_energy >= required_energy:
            self.state = f"UPDATED: {new_data}"
            return True, "Success: Energy harvest sufficient for state transition."
        else:
            return False, "Fail: Low entropy energy - Thermodynamic gate locked."

# --- SIMULATION RUN ---
if __name__ == "__main__":
    # 1. Initialize pFDO with a unique signal fingerprint (Physical Epitope)
    my_asset = PFDOObject("PID:2026:ASSET_001", physical_epitope=[0.123, 0.456, 0.789])

    print(f"--- pFDO Status: {my_asset.id} ---")

    # 2. Simulate an unauthorized remote access attempt (MIP Check)
    print("\n[Scenario 1: Remote Hijack Attempt]")
    is_secure = my_asset.verify_mip([0.999, 0.999, 0.999], rssi=-90)
    print(f"MIP Verification: {'PASSED' if is_secure else 'FAILED (Access Denied: Physical Boundary Breach)'}")

    # 3. Simulate a legitimate near-field energy harvesting event
    print("\n[Scenario 2: Near-field Legitimate Access]")
    if my_asset.verify_mip([0.124, 0.455, 0.790], rssi=-45):
        print("MIP Verification: PASSED")
        # Attempt to update state with insufficient energy
        success, msg = my_asset.update_state("New Location Data", harvested_energy=0.2)
        print(f"Update Result: {msg}")
        
        # Attempt to update state with sufficient energy
        success, msg = my_asset.update_state("New Location Data", harvested_energy=1.5)
        print(f"Update Result: {msg}")

    print(f"\nFinal pFDO State: {my_asset.state}")
