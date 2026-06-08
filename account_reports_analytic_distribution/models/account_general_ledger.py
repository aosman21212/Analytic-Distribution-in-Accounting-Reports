import json

from odoo import models
from odoo.tools import SQL


class AccountGeneralLedgerReportHandlerAnalytic(models.AbstractModel):
    """Extends the General Ledger custom engine to include an
    Analytic Distribution column at the journal-entry-line level.
    """
    _inherit = 'account.general.ledger.report.handler'

    def _report_custom_engine_general_ledger(
        self, expressions, options, date_scope,
        current_groupby, next_groupby,
        offset=0, limit=None, warnings=None,
    ):
        result = super()._report_custom_engine_general_ledger(
            expressions, options, date_scope,
            current_groupby, next_groupby,
            offset=offset, limit=limit, warnings=warnings,
        )

        if current_groupby == 'id_with_accumulated_balance':
            # ------------------------------------------------------------------
            # At the deepest groupby level every key encodes [date, aml_id].
            # We batch-fetch analytic_distribution for those ids in one query.
            # ------------------------------------------------------------------
            aml_id_to_entry = {}
            for key, entry in result:
                if 'balance_line' not in str(key):
                    try:
                        parsed = json.loads(key)
                        aml_id_to_entry[parsed[1]] = entry
                    except (ValueError, IndexError, TypeError):
                        pass

            if aml_id_to_entry:
                self.env.cr.execute(SQL(
                    "SELECT id, analytic_distribution"
                    " FROM account_move_line"
                    " WHERE id IN %s",
                    tuple(aml_id_to_entry.keys()),
                ))
                for row in self.env.cr.dictfetchall():
                    entry = aml_id_to_entry.get(row['id'])
                    if entry is not None:
                        entry['analytic_distribution'] = (
                            self._format_analytic_distribution(
                                row['analytic_distribution']
                            )
                        )

            # Set None on every entry that has no analytic distribution yet
            # (balance-line entries, or AML lines without any analytic).
            for _key, entry in result:
                entry.setdefault('analytic_distribution', None)

        elif isinstance(result, dict):
            # No groupby → total-line dict
            result.setdefault('analytic_distribution', None)

        else:
            # account_id groupby or any other aggregate level
            for _key, entry in result:
                entry.setdefault('analytic_distribution', None)

        return result
