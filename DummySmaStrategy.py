# region imports
from AlgorithmImports import *
# endregion

class DummySmaStrategy(QCAlgorithm):
	symbols = []
	holdings = {}

	def Initialize(self):
		self.symbols = self.GetParameter("Symbols").split(",")
		
		if eval(self.GetParameter("Training")):
			self.SetStartDate(2010, 1, 1)
			self.SetEndDate(2020, 5, 31)
		else:
			self.SetStartDate(2020, 6, 1)
			
		for ticker in self.symbols:
			symbol = self.AddEquity(ticker, Resolution.Daily).Symbol
			smaShortTerm = self.SMA(ticker, self.GetParameter("SmaShortTerm"), Resolution.Daily)
			smaLongTerm = self.SMA(ticker, self.GetParameter("SmaLongTerm"), Resolution.Daily)
			self.holdings.update({ticker: TickerInfo(symbol, smaShortTerm, smaLongTerm)})

		self.SetWarmup(int(self.GetParameter("SmaLongTerm")))
		self.SetCash(int(self.GetParameter("StartingCash")))
		self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Cash)
		self.SetBenchmark("SPY")

	def OnData(self, data):
		for ticker in self.symbols:
			try:
				indicator = self.holdings[ticker]

				if self.Portfolio[ticker].Invested:
					if not indicator.SmaShortTermWin[1] is None and not indicator.SmaLongTermWin[1] is None and indicator.SmaShortTermWin[1] > indicator.SmaLongTermWin[1] and indicator.SmaShortTermWin[0] < indicator.SmaLongTermWin[0]:
						self.SetHoldings(ticker, 0)
				else:
					if not indicator.SmaShortTermWin[1] is None and not indicator.SmaLongTermWin[1] is None and indicator.SmaShortTermWin[1] < indicator.SmaLongTermWin[1] and indicator.SmaShortTermWin[0] > indicator.SmaLongTermWin[0]:
						self.SetHoldings(ticker, 1 - (float(len(self.symbols) - self.Portfolio.Count) / len(self.symbols)))
			except:
				continue

class TickerInfo:
	def __init__(self, symbol, SmaShortTerm, SmaLongTerm):
		self.symbol = symbol
		self.SmaShortTerm = SmaShortTerm
		self.SmaShortTerm.Updated += self.SmaShortTermUpdated
		self.SmaShortTermWin = RollingWindow[IndicatorDataPoint](2)
		self.SmaLongTerm = SmaLongTerm
		self.SmaLongTerm.Updated += self.SmaLongTermUpdated
		self.SmaLongTermWin = RollingWindow[IndicatorDataPoint](2)

	def SmaShortTermUpdated(self, sender, updated):
		self.SmaShortTermWin.Add(updated)

	def SmaLongTermUpdated(self, sender, updated):
		self.SmaLongTermWin.Add(updated)