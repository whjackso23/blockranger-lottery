from utils.utils import get_account, get_contract, fund_contract_w_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()
    # the Lottery contract neds a lot of arguments

    # priceFeedAddress, etc.
    # so were gonna put all that argument fetching into a contract called "get_contract"
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print("Deployed that mf lottery boiiii")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lotto!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # remember the endLottery function needs to call the randomness function, which required LINK tokens
    tx = fund_contract_w_link(lottery.address)
    tx.wait(1)

    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)

    print("Lottery ended! Now we wait for Chainlink respond")
    # we need to wait for chainlink to respond...but this requires blocks to be finished
    time.sleep(10)
    print(f"Winner is {lottery.recentWinner()}")


def main():

    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
