from typing import TYPE_CHECKING

from rotkehlchen.chain.evm.manager import EvmManager

from .decoding.decoder import GnosisTransactionDecoder
from .tokens import GnosisTokens
from .transactions import GnosisTransactions

if TYPE_CHECKING:

    from .node_inquirer import GnosisInquirer


class GnosisManager(EvmManager):

    def __init__(
            self,
            node_inquirer: 'GnosisInquirer',
    ) -> None:
        transactions = GnosisTransactions(
            gnosis_inquirer=node_inquirer,
            database=node_inquirer.database,
        )
        super().__init__(
            node_inquirer=node_inquirer,
            transactions=transactions,
            tokens=GnosisTokens(
                database=node_inquirer.database,
                gnosis_inquirer=node_inquirer,
            ),
            transactions_decoder=GnosisTransactionDecoder(
                database=node_inquirer.database,
                gnosis_inquirer=node_inquirer,
                transactions=transactions,
            ),
        )
        self.node_inquirer: 'GnosisInquirer'  # just to make the type specific
