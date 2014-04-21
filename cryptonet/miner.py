import threading
import time

from cryptonet.debug import *

class Miner:
    def __init__(self, chain, seeknbuild):
        self._shutdown = False
        self._restart = False
        self.threads = [threading.Thread(target=self.mine)]
        self.chain = chain
        self.chain.set_miner(self)
        self.seeknbuild = seeknbuild
        
    def run(self):
        for t in self.threads:
            t.start()
        
    def shutdown(self):
        self._shutdown = True
        for t in self.threads:
            t.join()
        
    def restart(self):
        self._restart = True
        
    def mine(self, providedBlock=None):
        while not self._shutdown:
            if providedBlock == None: block = self.chain.head.get_candidate(self.chain)
            else: 
                block = providedBlock
                providedBlock = None
            count = 0
            print('miner restarting')
            while not self._shutdown and not self._restart:
                count += 1
                block.increment_nonce()
                if block.valid_proof_of_work():
                    break
                if count % 100000 == 0:
                    self._restart = True
            if self._shutdown: break
            if self._restart: 
                self._restart = False
                time.sleep(0.01)
                continue
            debug('Miner: Found Soln : %064x' % block.get_hash())
            debug('Miner: ser\'d block: ', block.serialize())
            self.seeknbuild.add_block(block)
            while not self.chain.has_block_hash(block.get_hash()) and not self._shutdown:
                time.sleep(0.1)
