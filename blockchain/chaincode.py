# blockchain/chaincode.py

from fabric_contract_api import Contract

class MedGuardChaincode(Contract):

    def __init__(self):
        super().__init__()

    def register_drug_batch(self, ctx, batch_number, drug_name, manufacturer, mfg_date, expiry_date):
        """
        Adds a new drug batch to the blockchain ledger.
        This function would typically only be callable by a Manufacturer role.
        """
        if self._asset_exists(ctx, batch_number):
            raise Exception(f"The drug batch {batch_number} already exists.")

        drug_asset = {
            "docType": "drug",
            "batchNumber": batch_number,
            "drugName": drug_name,
            "manufacturer": manufacturer,
            "mfgDate": mfg_date,
            "expiryDate": expiry_date,
            "owner": manufacturer,  # The manufacturer is the initial owner
            "history": [f"Registered by {manufacturer} on {ctx.get_tx_timestamp()}"]
        }
        ctx.get_stub().put_state(batch_number, bytes(str(drug_asset), 'utf-8'))
        return str(drug_asset)

    def transfer_drug_ownership(self, ctx, batch_number, new_owner):
        """
        Transfers ownership of a drug batch to a new entity (e.g., a distributor or pharmacy).
        """
        drug_asset = self._get_asset(ctx, batch_number)
        if not drug_asset:
            raise Exception(f"The drug batch {batch_number} does not exist.")

        previous_owner = drug_asset["owner"]
        drug_asset["owner"] = new_owner
        drug_asset["history"].append(f"Transferred from {previous_owner} to {new_owner} on {ctx.get_tx_timestamp()}")
        
        ctx.get_stub().put_state(batch_number, bytes(str(drug_asset), 'utf-8'))
        return str(drug_asset)

    def query_drug_history(self, ctx, batch_number):
        """
        Retrieves the complete ownership history of a drug batch.
        """
        drug_asset = self._get_asset(ctx, batch_number)
        if not drug_asset:
            raise Exception(f"The drug batch {batch_number} does not exist.")
        
        return drug_asset["history"]

    def _get_asset(self, ctx, asset_id):
        asset_bytes = ctx.get_stub().get_state(asset_id)
        if not asset_bytes or len(asset_bytes) == 0:
            return None
        return eval(asset_bytes.decode('utf-8')) # Using eval for simplicity in this example

    def _asset_exists(self, ctx, asset_id):
        return ctx.get_stub().get_state(asset_id) is not None