# from brownie import Lottery, accounts, config, network
# from scripts.deploy_lottery import deploy_lottery
# from web3 import Web3


# def test_get_entrance_fee():

#     acocunt = accounts[0]
#     lottery = Lottery.deploy(
#         config["networks"][network.show_active()]["eth_usd_price_feed"],
#         {"from": account},
#     )
#     assert lottery.getEntranceFee() > Web3.toWei(0.018, "ether")
