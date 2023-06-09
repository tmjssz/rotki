from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rotkehlchen.db.drivers.gevent import DBConnection

def globaldb_data_migration_2(conn: 'DBConnection') -> None:
    """Introduced at 1.xx.x
    - Add contract data for gnosis
    """
    with conn.write_ctx() as cursor:
        # Fetch abi ids from the entries for optimism
        cursor.execute('SELECT id from contract_abi WHERE name=?', ('BALANCE_SCAN',))
        balancescan_abi_id = cursor.fetchone()[0]
        cursor.execute('SELECT id from contract_abi WHERE name=?', ('MULTICALL2',))
        multicall_abi_id = cursor.fetchone()[0]
        cursor.execute('SELECT id from contract_abi WHERE name=?', ('DS_PROXY_REGISTRY',))
        ds_registry_abi_id = cursor.fetchone()[0]

        cursor.executemany(
            'INSERT INTO contract_data(address, chain_id, name, abi, deployed_block) '
            'VALUES(?, ?, ?, ?, ?)',
            [(
                '0x571C62a1c863aEAD01c1d34D8cB3Ee2c6f938800',
                100,
                'BALANCE_SCAN',
                balancescan_abi_id,
                14712144,
            ), (
                '0xcA11bde05977b3631167028862bE2a173976CA11',
                100,
                'MULTICALL2',
                multicall_abi_id,
                21022491,
            ), (
                '0x46AD1cB076f43126B9a89FdC06f3C8FdF3EEe6e5',
                100,
                'DS_PROXY_REGISTRY',
                ds_registry_abi_id,      
                16465065,
            )],
        )

