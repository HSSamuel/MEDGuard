# backend/blockchain_utils.py

# This is a placeholder for a real Hyperledger Fabric SDK client.
# In a full implementation, this would involve connecting to the peer nodes,
# selecting a channel, and invoking the chaincode.

def invoke_chaincode(function_name, *args):
    """
    Simulates invoking a function on the MedGuardChaincode.
    Returns a simulated success message or raises an exception.
    """
    print(f"--- SIMULATING BLOCKCHAIN INVOCATION ---")
    print(f"Function: {function_name}")
    print(f"Arguments: {args}")

    # In a real application, this would be a network call to the blockchain.
    # We simulate a successful transaction here.
    if function_name == "register_drug_batch":
        return {"status": "SUCCESS", "message": f"Successfully registered batch {args[0]} on the blockchain."}
    if function_name == "transfer_drug_ownership":
         return {"status": "SUCCESS", "message": f"Successfully transferred batch {args[0]} to {args[1]}."}
    
    return {"status": "ERROR", "message": "Function not found"}

def query_chaincode(function_name, *args):
    """
    Simulates querying a function on the MedGuardChaincode.
    Returns simulated data.
    """
    print(f"--- SIMULATING BLOCKCHAIN QUERY ---")
    print(f"Function: {function_name}")
    print(f"Arguments: {args}")

    if function_name == "query_drug_history":
        # Simulate a typical supply chain journey
        return [
            "Registered by HealthWell Inc. on 2025-09-28 10:00:00",
            "Transferred from HealthWell Inc. to Metro Distributors on 2025-09-29 14:30:00",
            "Transferred from Metro Distributors to City Pharmacy on 2025-09-30 09:15:00"
        ]
    
    return []