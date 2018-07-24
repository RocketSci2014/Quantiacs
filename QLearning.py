import numpy as np

class QModel:
    def __init__(self, nStates):
        self.Q = np.zeros((nStates, 3))
        self.limits = np.zeros(nStates - 1) #size nState - 1 to descrete the array
        self.nStates = nStates
    
    def update(self, currentState, nextState, reward, action, gamma):
        maxIndex = np.where(self.Q[nextState,] == np.max(self.Q[nextState,]))[0]
        
        if maxIndex.shape[0] > 1:
            maxIndex = int(np.random.choice(maxIndex, size = 1))
        else:
            maxIndex = int(maxIndex)
            
        maxValue = self.Q[nextState, maxIndex]
        self.Q[currentState, action] = reward + gamma * maxValue
        
        if (np.max(self.Q) > 0):
            return np.sum(self.Q / np.max(self.Q) * 100)
        else:
            return 0;
        
    def pridict(self, price):
        state = 0
        while state < 19 and self.limits[state] <= price:
            state += 1
                
        nextAction = np.where(self.Q[state,] == np.max(self.Q[state,]))[0]
        if nextAction.shape[0] > 1:
            nextAction = int(np.random.choice(nextAction, size = 1))
        else:
            nextAction = int(nextAction)
            
        return nextAction - 1
    
### just invest in one ticker
def createAndTrain(CLOSE, settings):
    
    #calculate price data and return
    priceData = CLOSE[:-1, 0]
    average = np.average(priceData)
    stdDev = np.std(priceData)
    priceData = (priceData - average) / stdDev
    returnData = (CLOSE[1:, 0] - CLOSE[:- 1, 0]) / CLOSE[:- 1, 0] #only track daily return
    
    #quntize
    nState = 50
    model = QModel(nState)
    length = priceData.shape[0]
    batchSize = length / nState
    sortedInd = np.argsort(priceData)
    quants = np.zeros((length, 1), dtype = 'int')
    
    for i in range(nState):
        if i < nState - 1:
            indices = sortedInd[i * batchSize : (i + 1) * batchSize]
            model.limits[i] = priceData[(i + 1) * batchSize]
            quants[indices] = i
        else:
            indices = sortedInd[i * batchSize :]
            quants[indices] = i
        
    #train the model
    for i in range(length - 1):
        gamma = 0.8
        state = int(quants[i])
        nextState = int(quants[i + 1])    
        reward = returnData[i] 
        
        if reward > 0:
            action = 2
        elif reward == 0:
            action = 1
        else:
            action = 0
        
        reward *= (action - 1)        
        score = model.update(state, nextState, reward, action, gamma)
        print score

    settings['mean'] = average
    settings['std'] = stdDev
    settings['model'] = model
    return


##### Do not change this function definition #####
def myTradingSystem(DATE, CLOSE, exposure, equity, settings):
    ''' This system uses mean reversion techniques to allocate capital into the desired equities '''
    lookBack = settings['lookback']
    if False == settings.has_key('model'):
        createAndTrain(CLOSE[:lookBack - 1], settings)

    model = settings['model']
    average = settings['mean']
    std_dev = settings['std']

    price = (CLOSE[-1] - average) / std_dev
    nextAction = model.pridict(price)
    nMarkets = CLOSE.shape[1]
    pos = np.zeros(nMarkets)
    pos[0] = nextAction 
    
    return pos, settings

##### Do not change this function definition #####
def mySettings():
    ''' Define your trading system settings here '''
    settings = {}

    # Futures Contracts
    settings['markets'] = ['F_ES']
    settings['slippage'] = 0.05
    settings['budget'] = 1000000
    settings['lookback'] = 504
    settings['beginInSample'] = '19920101'
    settings['endInSample'] = '20170101'

    return settings


# Evaluate trading system defined in current file.
if __name__ == '__main__':
    import quantiacsToolbox
    np.random.seed(98274534)

    results = quantiacsToolbox.runts(__file__, True)
    print('done')