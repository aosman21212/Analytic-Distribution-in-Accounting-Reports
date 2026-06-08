from odoo import models


class AccountReportCustomHandlerAnalytic(models.AbstractModel):
    """Extends the base report custom handler with a helper to format
    analytic_distribution JSON values into a human-readable string.
    All concrete handlers (General Ledger, Partner Ledger, …) inherit
    this method automatically.
    """
    _inherit = 'account.report.custom.handler'

    def _format_analytic_distribution(self, analytic_distribution):
        """Convert an analytic_distribution dict to a readable string.

        :param analytic_distribution: dict like {"account_id": percentage, …} or None
        :return: formatted string, e.g. "Marketing (60%), Sales (40%)" or None
        """
        if not analytic_distribution:
            return None

        account_ids = [int(k) for k in analytic_distribution.keys()]
        accounts = self.env['account.analytic.account'].browse(account_ids)
        account_names = {account.id: account.display_name for account in accounts}

        parts = []
        for account_id_str, percentage in analytic_distribution.items():
            account_id = int(account_id_str)
            name = account_names.get(account_id, str(account_id))
            if percentage == 100.0:
                parts.append(name)
            else:
                parts.append(f"{name} ({percentage:.0f}%)")

        return ', '.join(parts) or None
