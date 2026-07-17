from app.services.asset_returner import AssetsReturner
from app.services.risk import RiskScoring
from app.services.report_generator import ReportGenerator
from app.schemas.ask_request import AskRequest

class ReportAgent:

    def __init__(self):

        self.query = AssetsReturner()
        self.risk = RiskScoring()
        self.report = ReportGenerator()



    def run(self, question: AskRequest):

        result = self.query.run_query(question)
        returned_assets = result["rows"]

        if not returned_assets:
            return {
                "message": "No matching Assets Found"
            }
        
        risk_results = []
        for asset in returned_assets:
            asset_risk = self.risk.cal_risk(asset)
            risk_results.append(asset_risk)


        report = self.report.generate(question, returned_assets, risk_results)

        return report