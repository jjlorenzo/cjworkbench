from .moduleimpl import ModuleImpl


class ReorderFromTable(ModuleImpl):
    @staticmethod
    def render(params, table, **kwargs):
        # Entries should appear in chronological order as new
        # operations are appended to the end of the stack
        history_entries = params.get_param_json('reorder-history')

        if not history_entries:
            return table  # no reorders

        columns = table.columns.tolist()

        for entry in history_entries:
            from_idx = int(entry['from'])
            to_idx = int(entry['to'])

            # Our original input columns can get moved or deleted, but we'll
            # give it a shot if indices are in range
            if from_idx >= len(columns) or to_idx >= len(columns):
                continue

            moved = columns.pop(from_idx)
            columns.insert(to_idx, moved)

        return table[columns]
