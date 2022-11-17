from lspscript.client import Client, StdIOConnectionParams
from pytest import raises, mark

# Not to be confused with the TimeoutError(OSError)
from asyncio.exceptions import TimeoutError

@mark.slow
async def test_client_timeout_fail() -> None:
    params = StdIOConnectionParams(launch_command="node mock-server/out/index.js --stdio test/test_client_timeout.json")
    async with Client(params) as client:
        with raises(TimeoutError):
            await client.send_request("$/sleep", 4.0, timeout=2.0)


@mark.slow
async def test_client_timeout_indefinite() -> None:
    params = StdIOConnectionParams(launch_command="node mock-server/out/index.js --stdio test/test_client_timeout.json")
    async with Client(params) as client:
        await client.send_request("$/sleep", 4.0, timeout=None)
