# vi: ai ts=4 sw=4 et

'''Provide objects for use in Behave tests.'''

import logging
from behave import fixture, use_fixture
from behave.api.async_step import use_or_create_async_context
from steps.echoclient import EchoClientProtocol

async def init_transport(context, async_context, on_con_lost):
    '''Initiate network transport.

    :param context: Behave test context.
    :param async_context: Async context for asyncio operations.
    :param on_con_lost: Future for signaling loss of connection.
    '''
    logging.info('start_client')
    transport, protocol = \
        await async_context.loop.create_datagram_endpoint(
            lambda: EchoClientProtocol(on_con_lost),
            remote_addr=('127.0.0.1', 9999))
    context.echo = (transport, protocol)

@fixture
def udp_transport(context):
    '''Fixture to provide network transport for tests.

    :param context: Behave test context.
    '''
    logging.info('fixture udp_transport')
    async_context = use_or_create_async_context(context, 'udp_transport')
    on_con_lost = async_context.loop.create_future()

    # Create the task for the client
    task = async_context.loop.create_task(
        init_transport(context, async_context, on_con_lost))
    async_context.loop.run_until_complete(task)
    assert hasattr(context, 'echo')

    yield getattr(context, 'echo')
    context.echo[0].close()

def before_scenario(context, scenario):
    '''Before each scenario, set up environment.'''
    pass

def before_feature(context, feature):
    '''Before each feature, set up environment.'''
    use_fixture(udp_transport, context)
