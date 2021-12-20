from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery, get_contract
from utils.utils import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_contract_w_link,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():

    # Arrange (?)
    lottery = deploy_lottery()

    # Act (?)
    # price of Eth is ~4500
    # so...a USD entry fee of 50 would be approx .0115
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():

    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    # Act/ Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():

    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_contract_w_link(lottery)
    lottery.endLottery({"from": account})

    # since 'CALCULATING_WINNER' in in position 2 in the array (third item)
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    fund_contract_w_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777

    # now we have to pretend we're link and get a random number
    random_numb = get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )

    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    # 777 mod 3 will be 0 so the first account will be the winner
    assert lottery.recentWinner() == get_account(index=1)
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
