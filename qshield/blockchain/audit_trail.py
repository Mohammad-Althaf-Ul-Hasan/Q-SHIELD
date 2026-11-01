"""
audit_trail.py
Immutable blockchain‑based key event audit trail.

Each time a key is generated or compromised, an event is recorded
in a block. The chain is append‑only and secured by SHA‑256 Proof‑of‑Work,
making it computationally infeasible to alter past records.

Reference: S. Nakamoto, "Bitcoin: A Peer‑to‑Peer Electronic Cash System", 2008.
"""

import hashlib
import json
import time
from typing import List, Optional


class Block:
    """A single block in the audit chain."""

    def __init__(
        self,
        index: int,
        timestamp: float,
        data: dict,
        previous_hash: str,
        nonce: int = 0,
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """SHA‑256 hash of the block contents."""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty: int = 2):
        """
        Perform Proof‑of‑Work: find a nonce such that the hash
        starts with `difficulty` zeros.
        """
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()


class Blockchain:
    """
    Immutable audit trail backed by a Proof‑of‑Work blockchain.
    """

    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the first block (genesis)."""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            data={'event': 'Q‑SHIELD Audit Trail Initialised'},
            previous_hash='0' * 64,
        )
        genesis.mine(self.difficulty)
        self.chain.append(genesis)

    def add_event(self, event_data: dict) -> Block:
        """
        Record a new event and append its block to the chain.

        Args:
            event_data: Dictionary with event details (e.g.
                        key_id, qber, status, session_id).

        Returns:
            The newly mined Block.
        """
        last_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=event_data,
            previous_hash=last_block.hash,
        )
        new_block.mine(self.difficulty)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        """Verify the integrity of the entire chain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check current block hash
            if current.hash != current.compute_hash():
                return False

            # Check link to previous block
            if current.previous_hash != previous.hash:
                return False

        return True

    def get_events(self, limit: int = 20) -> list:
        """Return the most recent events as a list of dicts."""
        return [
            {
                'index': b.index,
                'timestamp': b.timestamp,
                'hash': b.hash[:16],
                'data': b.data,
            }
            for b in self.chain[-limit:]
        ]

    def to_dict(self) -> dict:
        """Serialise the full chain to a dictionary."""
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'valid': self.is_chain_valid(),
            'chain': [
                {
                    'index': b.index,
                    'timestamp': b.timestamp,
                    'previous_hash': b.previous_hash,
                    'hash': b.hash,
                    'nonce': b.nonce,
                    'data': b.data,
                }
                for b in self.chain
            ],
        }


# Global instance (will be initialised by app.py)
audit_chain = Blockchain(difficulty=2)