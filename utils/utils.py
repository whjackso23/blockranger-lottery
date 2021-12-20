from brownie import (
    network,
    config,
    accounts,
    MockV3Aggregator,
    LinkToken,
    VRFCoordinatorMock,
    Contract,
    interface,
)
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 18
STARTING_PRICE = 200_000_000_000


def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    Will grab the contract addresses from config, otherwise will deploy a mocked contract and return it

    args:
        contract_name(string)
    returns:
        contract (brownie.network.contract.ProjectContract: the most recently deployed version of this contract)
    """

    # need to map a contract name to type of contract
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
        # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract

    # ^^ is equivalent to saying MockV3Aggregator.length to see if any mocks have been deployed


def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("mocks Deployed!")


# default value is 0.1 LINK
def fund_contract_w_link(
    address, account=None, link_token=None, amount=100000000000000000
):

    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")

    # the more hands on method
    tx = link_token.transfer(address, amount, {"from": account})
    tx.wait(1)
    print("funded contract w LINK!")

    # # You can also use an interface!
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(address, amount, {"from": account})
    # tx.wait(1)
    # print("funded contract w LINK")

    return tx
