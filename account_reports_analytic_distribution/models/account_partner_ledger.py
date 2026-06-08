from odoo import models
from odoo.tools import SQL


class AccountPartnerLedgerReportHandlerAnalytic(models.AbstractModel):
    """Extends the Partner Ledger custom handler to include an
    Analytic Distribution column on every journal-entry line.

    The Partner Ledger only shows receivable/payable lines. In practice,
    analytic distributions are set on the income/expense counterpart lines
    of the same journal entry – not on the receivable/payable line itself.
    So we:
      1. Also fetch move_id + the AML's own analytic_distribution via the
         existing extension hook (_get_additional_column_aml_values).
      2. After the base query, batch-look up analytic distributions from
         all other lines of each move, for any AML that has no analytic
         of its own.
      3. Format and inject the result so _get_report_line_move_line renders
         it without any further changes.
    """
    _inherit = 'account.partner.ledger.report.handler'

    # ------------------------------------------------------------------
    # 1. Add move_id + analytic_distribution to every AML SELECT
    # ------------------------------------------------------------------
    def _get_additional_column_aml_values(self):
        parent_sql = super()._get_additional_column_aml_values()
        # move_id is a hidden helper column (no matching report column);
        # analytic_distribution is the visible one.
        return SQL(
            "%s account_move_line.move_id, account_move_line.analytic_distribution,",
            parent_sql,
        )

    # ------------------------------------------------------------------
    # 2. Enrich results: fall back to the move's analytic distribution
    #    when the receivable/payable line has none of its own
    # ------------------------------------------------------------------
    def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        rslt = super()._get_aml_values(
            options, partner_ids, offset=offset, limit=limit
        )

        # Collect entries that have no direct analytic_distribution, grouped
        # by the move they belong to.
        move_id_to_entries = {}
        for amls in rslt.values():
            for aml in amls:
                if not aml.get('analytic_distribution'):
                    move_id = aml.get('move_id')
                    if move_id:
                        move_id_to_entries.setdefault(move_id, []).append(aml)

        if move_id_to_entries:
            # Batch-fetch analytic distributions from the counterpart lines of
            # each move (e.g. the income/expense lines of an invoice).
            self.env.cr.execute(SQL(
                """
                SELECT move_id, analytic_distribution
                FROM account_move_line
                WHERE move_id IN %s
                  AND analytic_distribution IS NOT NULL
                  AND analytic_distribution::text != 'null'
                """,
                tuple(move_id_to_entries.keys()),
            ))
            # Merge all distributions found for the same move
            move_analytic = {}
            for row in self.env.cr.dictfetchall():
                mid = row['move_id']
                dist = row['analytic_distribution']
                if dist and isinstance(dist, dict):
                    combined = move_analytic.setdefault(mid, {})
                    combined.update(dist)

            # Inject the formatted string into the AML entry dicts
            for move_id, entries in move_id_to_entries.items():
                analytic = move_analytic.get(move_id)
                if analytic:
                    formatted = self._format_analytic_distribution(analytic)
                    for entry in entries:
                        entry['analytic_distribution'] = formatted

        # Format any AML that did have a direct analytic_distribution (dict → str)
        for amls in rslt.values():
            for aml in amls:
                raw = aml.get('analytic_distribution')
                if isinstance(raw, dict):
                    aml['analytic_distribution'] = self._format_analytic_distribution(raw)

        return rslt
