'''gpdht.py contains functions to validate the protocol'''

import hashlib, sys
import sha3
from binascii import hexlify, unhexlify

import cryptonet
from cryptonet.debug import *

#from utilities import *


#==============================================================================
# GENERAL CRYPTONET FUNCTIONS
#==============================================================================
    
i2b = lambda x : x.to_bytes((x.bit_length() // 8) + 1, 'big')

def num2bits(n, minlen=0):
    n = int(n)
    r = []
    while n > 0:
        r.append(n%2)
        n //= 2
    pad = minlen - len(r)
    while pad > 0:
        r.append(0)
        pad -= 1
    return r[::-1]

def valid_proof_of_work(ht, cd):
    return ht.get_hash() < cd.unpacked_target

def global_hash(msg):
    ''' This is the hash function that should be used EVERYWHERE in GPDHT.
    Currently defined to be SHA3.
    As always, should return a BANT '''
    s = hashlib.sha3_256()
    s.update(bytes(msg))
    return int.from_bytes(s.digest(), 'big')



def pack_target(unpacked_target):
    # TODO : test
    pad = 32 - len(unpacked_target)
    while unpacked_target[0] == 0:
        pad += 1
        unpacked_target = unpacked_target[1:]
    a = unpacked_target[:3] + bytearray([pad])
    return BANT(a)
    
def unpack_target(packed_target):
    # TODO : test
    packed_target = bytes(packed_target)
    pad = packed_target[3]
    sigfigs = packed_target[:3]
    rt = ZERO*pad + sigfigs + ZERO*(32-3-pad)
    return BANT(int(hexlify(rt),16))


#=========================
# CHAIN
#=========================

class Chain(object):
    ''' Holds a PoW chain and can answer queries '''
    # initial conditions must be updated when Chaindata structure updated
    
    def __init__(self, chain_vars, genesis_block=None, db=None, cryptonet=cryptonet):
        self.initialized = False
        self.cryptonet = cryptonet
        self._Block = self.cryptonet._Block
        self.head = None
        self.db = db
        self.miner = None
        self.blocks = set()
        self.block_hashes = set()
        
        self.genesis_block = None
        if genesis_block != None: self.set_genesis(genesis_block)
        
    def restart_miner(self):
        if self.miner != None:
            self.miner.restart()
        
    def set_miner(self, miner):
        self.miner = miner
    
    def hash(self, message):
        return global_hash(message)
        
    def set_genesis(self, block):
        if self.genesis_block == None:
            block.assert_validity(self)
            
            self.genesis_block = block
            self.head = block
            
            self.add_block(block)
        else:
            raise ChainError('genesis block already known: %s' % self.genesis_block)
        
    # added sigmadiff stuff, need to test
    def add_block(self, block):
        ''' returns True on success '''
        if self.has_block(block): return
        
        if block.better_than(self.head):
            self.head = block
            debug('chain: new head %d, hash: %064x' % (block.height, block.get_hash()))
        
        self.db.set_entry(block.get_hash(), block)
        self.db.set_ancestors(block)
        self.blocks.add(block)
        self.block_hashes.add(block.get_hash())
        
        
        if self.initialized == False:
            self.initialized = True
        
        debug('added block %d, hash: %064x' % (block.height, block.get_hash()))
        
        self.restart_miner()
        
        return True
        
    def get_block(self, block_hash):
        return self.db.get_entry(block_hash)
        
    def has_block(self, block):
        return block in self.blocks
          
    def has_block_hash(self, block_hash):
        return block_hash in self.block_hashes
    
    def valid_alert(self, alert):
        # TODO : not in PoC, probably not in GPDHTChain either
        # TODO : return True if valid alert
        pass
        
    
    def get_successors(self, blocks, stop):
        # TODO : not in PoC
        # TODO : Probably won't be used with new blockchain struct
        # TODO : find HCB and then some successors until stop or max num
        #return [self.db.get_successors(b) for b in blocks]
        pass
        
    def get_height(self):
        return self.head.height
        
    def get_top_block(self):
        return self.head
        
    def get_ancestors(self, start):
        return self.db.get_ancestors(start)
        
    def load_chain(self):
        # TODO : load chainstate from database
        pass
        #self.db.get_successors(self.genesisHash)
    
    def learnOfDB(self, db):
        self.db = db
        self.load_chain()

