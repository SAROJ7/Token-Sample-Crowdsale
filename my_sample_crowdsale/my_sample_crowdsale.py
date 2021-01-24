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
        self._balances = ArrayDB(self._BALANCES, db , value_type= int)
        self._joiner_list = VarDB(self._JOINER_LIST, db, value_type= Address)
        self._funding_goal_reached = VarDB(self._FUNDING_GOAL_REACHED, db, value_type=bool)
        self._crowdsale_closed = VarDB(self._CROWDSALE_CLOSED, db, value_type=bool)


    def on_install(self, fundingGoalInIcx: int, tokenScore: Address, durationInBlocks: int) -> None:
        super().on_install()

        Logger.debug(f'on_install: fundingGoalInIcx  = {fundingGoalInICX}', TAG)
        Logger.debug(f'on_install: tokenScore  = {tokenScore}', TAG)
        Logger.debug(f'on_install: durationInBlocks  = {fundingGoalInICX}', TAG)

    def on_update(self) -> None:
        super().on_update()
    
    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"
