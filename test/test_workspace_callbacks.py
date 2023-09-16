from asyncio import Event, wait_for
from typing import List

from change_ls import Client, StdIOConnectionParams, WorkspaceRequestHandler
from change_ls.types import (ApplyWorkspaceEditParams,
                             ApplyWorkspaceEditResult, ConfigurationParams,
                             DiagnosticSeverity, LSPAny,
                             PublishDiagnosticsParams, WorkspaceFolder)


class MockWorkspaceRequestHandler(WorkspaceRequestHandler):
    on_workspace_folders_event: Event
    on_configuration_event: Event
    on_semantic_tokens_refresh_event: Event
    on_inline_value_refresh_event: Event
    on_inlay_hint_refresh_event: Event
    on_diagnostic_refresh_event: Event
    on_code_lens_refresh_event: Event
    on_apply_edit_event: Event
    on_publish_diagnostics_event: Event

    def __init__(self) -> None:
        self.on_workspace_folders_event = Event()
        self.on_configuration_event = Event()
        self.on_semantic_tokens_refresh_event = Event()
        self.on_inline_value_refresh_event = Event()
        self.on_inlay_hint_refresh_event = Event()
        self.on_diagnostic_refresh_event = Event()
        self.on_code_lens_refresh_event = Event()
        self.on_apply_edit_event = Event()
        self.on_publish_diagnostics_event = Event()

    def on_workspace_folders(self) -> List[WorkspaceFolder]:
        self.on_workspace_folders_event.set()
        return [
            WorkspaceFolder(uri="file://test1", name="test1"),
            WorkspaceFolder(uri="file://test2", name="test2"),
        ]

    def on_configuration(self, params: ConfigurationParams) -> List[LSPAny]:
        assert len(params.items) == 2
        assert params.items[0].scopeUri == "file://config"
        assert params.items[0].section == "test-section-1"
        assert params.items[1].scopeUri == "file://config"
        assert params.items[1].section == "test-section-2"

        self.on_configuration_event.set()
        return ["Config-Thing-1", "Config-Thing-2"]

    def on_semantic_tokens_refresh(self) -> None:
        self.on_semantic_tokens_refresh_event.set()

    def on_inline_value_refresh(self) -> None:
        self.on_inline_value_refresh_event.set()

    def on_inlay_hint_refresh(self) -> None:
        self.on_inlay_hint_refresh_event.set()

    def on_diagnostic_refresh(self) -> None:
        self.on_diagnostic_refresh_event.set()

    def on_code_lens_refresh(self) -> None:
        self.on_code_lens_refresh_event.set()

    def on_apply_edit(self, params: ApplyWorkspaceEditParams) -> ApplyWorkspaceEditResult:
        assert params.label == "Random Change"
        assert params.edit.changes is not None
        assert "file://module_1" in params.edit.changes.keys()
        assert len(params.edit.changes["file://module_1"]) == 1
        assert params.edit.changes["file://module_1"][0].range.start.line == 1
        assert params.edit.changes["file://module_1"][0].range.start.character == 0
        assert params.edit.changes["file://module_1"][0].range.end.line == 1
        assert params.edit.changes["file://module_1"][0].range.end.character == 5
        assert params.edit.changes["file://module_1"][0].newText == "Hey"

        self.on_apply_edit_event.set()
        return ApplyWorkspaceEditResult(applied=True)

    def on_publish_diagnostics(self, params: PublishDiagnosticsParams) -> None:
        assert params.uri == "file://dignostic_test"
        assert len(params.diagnostics) == 1
        assert params.diagnostics[0].range.start.line == 1
        assert params.diagnostics[0].range.start.character == 0
        assert params.diagnostics[0].range.end.line == 1
        assert params.diagnostics[0].range.end.character == 5
        assert params.diagnostics[0].severity == DiagnosticSeverity.Information
        assert params.diagnostics[0].message == "This is a test"
        self.on_publish_diagnostics_event.set()


async def test_workspace_callbacks() -> None:
    params = StdIOConnectionParams(
        launch_command="node mock-server/out/index.js --stdio test/test_workspace_callbacks.json")
    async with Client(params) as client:
        handler = MockWorkspaceRequestHandler()
        client.set_workspace_request_handler(handler)

        client.send_notification("$/go", None)
        await wait_for(handler.on_workspace_folders_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_configuration_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_semantic_tokens_refresh_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_inline_value_refresh_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_inlay_hint_refresh_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_diagnostic_refresh_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_code_lens_refresh_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_apply_edit_event.wait(), 2.0)

        client.send_notification("$/go", None)
        await wait_for(handler.on_publish_diagnostics_event.wait(), 2.0)
