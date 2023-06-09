import logging
from typing import TYPE_CHECKING, Literal, cast

from eth_typing import BlockNumber

from rotkehlchen.chain.constants import DEFAULT_EVM_RPC_TIMEOUT
from rotkehlchen.chain.evm.contracts import EvmContracts
from rotkehlchen.chain.evm.node_inquirer import EvmNodeInquirerWithDSProxy
from rotkehlchen.chain.evm.types import string_to_evm_address
from rotkehlchen.constants.assets import A_ETH
from rotkehlchen.fval import FVal
from rotkehlchen.greenlets.manager import GreenletManager
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import (
    ChainID,
    ChecksumEvmAddress,
    EVMTxHash,
    SupportedBlockchain,
    Timestamp,
)

from .constants import (
    ARCHIVE_NODE_CHECK_ADDRESS,
    ARCHIVE_NODE_CHECK_BLOCK,
    ARCHIVE_NODE_CHECK_EXPECTED_BALANCE,
    GNOSIS_ETHERSCAN_NODE,
    GNOSIS_ETHERSCAN_NODE_NAME,
    PRUNED_NODE_CHECK_TX_HASH,
)
from .etherscan import GnosisEtherscan

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


class GnosisInquirer(EvmNodeInquirerWithDSProxy):

    def __init__(
            self,
            greenlet_manager: GreenletManager,
            database: 'DBHandler',
            rpc_timeout: int = DEFAULT_EVM_RPC_TIMEOUT,
    ) -> None:
        etherscan = GnosisEtherscan(
            database=database,
            msg_aggregator=database.msg_aggregator,
        )
        contracts = EvmContracts[Literal[ChainID.GNOSIS]](chain_id=ChainID.GNOSIS)
        super().__init__(
            greenlet_manager=greenlet_manager,
            database=database,
            etherscan=etherscan,
            blockchain=SupportedBlockchain.GNOSIS,
            etherscan_node=GNOSIS_ETHERSCAN_NODE,
            etherscan_node_name=GNOSIS_ETHERSCAN_NODE_NAME,
            contracts=contracts,
            rpc_timeout=rpc_timeout,
            contract_multicall=contracts.contract(string_to_evm_address('0x2DC0E2aa608532Da689e89e237dF582B783E552C')),  # noqa: E501
            contract_scan=contracts.contract(string_to_evm_address('0x1e21bc42FaF802A0F115dC998e2F0d522aDb1F68')),  # noqa: E501
            dsproxy_registry=contracts.contract(string_to_evm_address('0x283Cc5C26e53D66ed2Ea252D986F094B37E6e895')),  # noqa: E501
            native_token=A_ETH.resolve_to_crypto_asset(),
        )
        self.etherscan = cast(GnosisEtherscan, self.etherscan)

    # -- Implementation of EvmNodeInquirer base methods --

    def query_highest_block(self) -> BlockNumber:
        block_number = self.etherscan.get_latest_block_number()
        log.debug('Gnosis highest block result', block=block_number)
        return BlockNumber(block_number)

    def _get_pruned_check_tx_hash(self) -> EVMTxHash:
        return PRUNED_NODE_CHECK_TX_HASH

    def _get_archive_check_data(self) -> tuple[ChecksumEvmAddress, int, FVal]:
        return (
            ARCHIVE_NODE_CHECK_ADDRESS,
            ARCHIVE_NODE_CHECK_BLOCK,
            ARCHIVE_NODE_CHECK_EXPECTED_BALANCE,
        )

    def get_blocknumber_by_time(
            self,
            ts: Timestamp,
            etherscan: bool = True,
            closest: Literal['before', 'after'] = 'before',
    ) -> int:
        """Searches for the blocknumber of a specific timestamp

        May raise RemoteError
        """
        return self.etherscan.get_blocknumber_by_time(ts=ts, closest=closest)
