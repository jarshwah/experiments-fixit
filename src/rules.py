import libcst as cst
from fixit import LintRule


class Nothing(LintRule):
    def visit_Module(self, node: cst.Module) -> None:
        return None
