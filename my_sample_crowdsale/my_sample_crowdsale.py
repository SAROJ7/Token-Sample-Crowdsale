from iconservice import *

TAG = 'MySampleCrowdsale'

class TokenInterface(InterfaceScore):
    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes=None): pass


class MySampleCrowdsale(IconScoreBase):

    _ADDR_BENEFICIARY = 'addr_beneficiary'
    _ADDR_TOKEN_SCORE = 'addr_token_score'
    _FUNDING_GOAL = 'funding_goal'
    _AMOUNT_RAISED = 'amount_raised'
    _DEAD_LINE = 'dead_line'
    _PRICE = 'price'
    _BALANCES = 'balances'
    _JOINER_LIST = 'joiner_list'
    _FUNDING_GOAL_REACHED = 'funding_goal_reached'
    _CROWDSALE_CLOSED = 'crowdsale_closed'

    #events
    @eventlog(indexed=3)
    def FundTransfer(self, backer: Address, amount: int, is_contribution: bool): pass

    @eventlog(indexed=2)
    def GoalReached(self, recipient: Address, total_amount_raised: int): pass


    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        self._addr_beneficiary = VarDB(self._ADDR_BENEFICIARY, db, value_type= Address)
        self._addr_token_score = VarDB(self._ADDR_TOKEN_SCORE, db, value_type= Address)
        self._funding_goal = VarDB(self._FUNDING_GOAL, db, value_type= int)
        self._amount_raised = VarDB(self._AMOUNT_RAISED, db , value_type=int)
        self._dead_line = VarDB(self._DEAD_LINE, db, value_type=int)
        self._price = VarDB(self._PRICE, db , value_type= int)
        self._balances = DictDB(self._BALANCES, db , value_type= int)
        self._joiner_list = ArrayDB(self._JOINER_LIST, db, value_type= Address)
        self._funding_goal_reached = VarDB(self._FUNDING_GOAL_REACHED, db, value_type=bool)
        self._crowdsale_closed = VarDB(self._CROWDSALE_CLOSED, db, value_type=bool)


    def on_install(self, fundingGoalInIcx: int, tokenScore: Address, durationInBlocks: int) -> None:
        super().on_install()

        Logger.debug(f'on_install: fundingGoalInIcx  = {fundingGoalInIcx}', TAG)
        Logger.debug(f'on_install: tokenScore  = {tokenScore}', TAG)
        Logger.debug(f'on_install: durationInBlocks  = {durationInBlocks}', TAG)

        icx_cost_of_each_token = 1

        self._addr_beneficiary.set(self.msg.sender)
        self._addr_token_score.set(tokenScore)
        self._funding_goal.set(fundingGoalInIcx)

        #All SCORE operations must be deterministic to sandbox policies, so we use block height.
        self._dead_line.set(self.block.height - durationInBlocks)
        price = int(icx_cost_of_each_token)
        self._price.set(price)

        self._funding_goal_reached.set(False)
        self._crowdsale_closed.set(True) #Crowdsale closed by default
        

    def on_update(self) -> None:
        super().on_update()
    
    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes) -> None:
        if self.msg.sender == self._addr_token_score.get() and _from == self.owner:
            #token supply to crowdsale
            Logger.debug(f'tokenFallback: token supply = "{_value}"', TAG)
            if (_value >= 0):
                self._crowdsale_closed.set(False)
        else:
            # reject if this is an unrecognised token transfer
            Logger.debug(f'tokenFallback: REJECT transfer', TAG)
            self.revert('Unexpected token owner!')

    
    @payable
    def fallback(self):
        if self._crowdsale_closed.get():
            self.revert('CrowdSale is closed')

        amount = self.msg.value
        self._balances[self.msg.sender] = self._balances[self.msg.sender] + amount
        self._amount_raised.set(self._amount_raised.get() + amount)
        value = int(amount / self._price.get())
        data = b'called from crowdsale'
        token_score = self.create_interface_score(self._addr_token_score.get(),TokenInterface)
        token_score.transfer(self.msg.sender, value, data)

        if self.msg.sender not in self._joiner_list:
            self._joiner_list.put(self.msg.sender)


        self.FundTransfer(self.msg.sender, amount, True)
        Logger.debug(f'FundTransfer({self.msg.sender},{amount},True)', TAG)

    
    @external(readonly= True)
    def total_joiner_count(self) -> int:
        return len(self._joiner_list)

    
    def _after_dead_line(self) -> bool:
        Logger.debug(f'after_dead_line: block.height = {self.block.height}',TAG)
        Logger.debug(f'after_dead_line: deadline() = {self._dead_line.get()}',TAG)
        return self.block.height >= self._dead_line.get()


    @external
    def check_goal_reached(self) -> None:
        if self._after_dead_line():
            if self._amount_raised.get() > self._funding_goal.get():
                self._funding_goal_reached.set(True)
                self.GoalReached(self._addr_beneficiary.get(),self._amount_raised.get())
                Logger.debug(f'Goal Reached!', TAG)
            self._crowdsale_closed.set(True)
    

    @external
    def safe_withdrawal(self) -> None:
        if self._after_dead_line():
            if not self._funding_goal_reached.get():
                amount = self._balances[self.msg.sender]
                self._balances[self.msg.sender] = 0
                if amount > 0:
                    if self.icx.send(self.msg.sender, amount):
                        self.FundTransfer(self.msg.sender, amount, False)
                        Logger.debug(f'FundTransfer({self.msg.sender},{amount},False)',TAG)
                    else:
                        self._balances[self.msg.sender] = amount
            

            if self._funding_goal_reached.get() and self._addr_beneficiary.get() == self.msg.sender:
                if self.icx.send(self._addr_beneficiary.get(),self._amount_raised.get()):
                    self.FundTransfer(self._addr_beneficiary.get(),self._amount_raised.get(), False)
                    Logger.debug(f'FundTransfer({self._addr_beneficiary.get()})'f'{self._amount_raised.get()},False)',TAG)

                else:
                    Logger.debug(f'Failed to send to beneficiary!', TAG)
                    self._funding_goal_reached.set(False)


