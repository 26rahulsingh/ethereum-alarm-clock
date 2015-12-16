deploy_contracts = [
    "Scheduler",
    "TestCallExecution",
    "TestDataRegistry",
]


def test_cannot_schedule_with_too_small_grace_perioud(deploy_client, deployed_contracts,
                                                      deploy_future_block_call, denoms,
                                                      SchedulerLib):
    scheduler = deployed_contracts.Scheduler
    client_contract = deployed_contracts.TestCallExecution

    minimum_grace_period = scheduler.get_minimum_grace_period()
    now_block = deploy_client.get_block_number()

    scheduling_txn = scheduler.schedule_call(
        client_contract._meta.address,
        client_contract.setBool.encoded_abi_signature,
        now_block + 40 + 10 + 255,
        1000000,
        minimum_grace_period - 1,
        value=10 * denoms.ether,
        gas=3000000,
    )
    scheduling_receipt = deploy_client.wait_for_transaction(scheduling_txn)

    call_rejected_logs = SchedulerLib.CallRejected.get_transaction_logs(scheduling_txn)
    assert len(call_rejected_logs) == 1
    call_rejected_data = SchedulerLib.CallRejected.get_log_data(call_rejected_logs[0])

    assert call_rejected_data['reason'] == 'GRACE_TOO_SHORT'
