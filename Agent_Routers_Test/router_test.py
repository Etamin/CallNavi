from langchain_community.llms import Ollama
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch
from langchain_community.chat_models import ChatAnthropic
from langchain.chains import APIChain
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import outlines
llm = Ollama(
    base_url="http://trux-dgx01.uni.lux:11434",
    model="mistral"
)  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

#SQL DB Info
db = SQLDatabase.from_uri("sqlite:///bank.sqlite")
execute_query = QuerySQLDataBaseTool(db=db)


# multi_prompt="""
# Given the user question below, and the rules, classify and create a pipeline in correct order select from 1 to 5. 

# Only answer the such step+step as "1+2" or 1 step as "1".
# Give the correct order of operation.
# Then give the question of each step when we ask other models.
# """



api_doc="""
info:
  version: 1.0.0
  title: customer
  description: 'A client info retrieval API, get client account number from his/her name.'

servers:
  - url: http://trux-dgx01.uni.lux:5000/
    description: Local test server

paths:
  # Retrieve the bank account number
  /data
    get:
      description: Find account number from name.
      summary: Find account number from name.
      parameters:
        - name: name
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successfully returned an account number
          content:
            application/json:
"""


# API Caller
# apicaller=APIChain.from_llm_and_api_docs(
#     llm,
#     api_doc,
#     verbose=True,
#     limit_to_domains=None,
#     API_URL_PROMPT_TEMPLATE = """You are given the below API Documentation:
# {api_docs}
# Using this documentation, generate the full API url to call for answering the user question.
# You should build the API url to get a response that is as short as possible, while still getting the necessary information to answer the question. Pay attention to deliberately exclude any unnecessary pieces of data in the API call. Return only the URL without any additional explanation or context.
# DON'T give me anything except the one line URL!!!
# Question:{question}
# API url:"""
# )
template1='''<template>
{
  "name": "David"
}
</template>'''

template2='''
<template>
{ "user_id" = id_value, "date" = date}
</template>
'''

apicaller=(PromptTemplate.from_template(
'''
{template}
Using this API JSON call parameter template, generate the API call parameter JSON to answering the user question.
You should build the API JSON to get a response that is follow the format above.
ONLY answer the JSON string same as template, no explanation.
<question>
{question}
</question>

API JSON:"""
'''
  )
    | llm
    | StrOutputParser()
)


# Router Gene
# router_chain = (
#     PromptTemplate.from_template(
#         """
# We have these tools in our platform, here is their functions and 
# 1, API: give customer name, get the ID or give ID get;
# 2, SQL: get customer transaction record, only with his/her ID;
# 3, Translator: translate other languages to English;
# 4, RAG: other common questions or document retrieval;
# 5, Summary: summarize text;
        
# Given the user question below, and the rules, classify and give a correct next step from  1 to 5. 

# Only answer with one number.

# <question>
# {question}
# </question>

# Classification:"""
#     )
#     | llm
#     | StrOutputParser()
# )

router_chain = (
    PromptTemplate.from_template(
        """
We have these API in our platform, here are their name and function:

createCustomer,Creates a new customer profile in the system.
updateCustomerInfo,Updates existing customer information.
getCustomerDetails,Retrieves detailed information about a specific customer.
listCustomers,Returns a list of all customers with optional filtering.
deleteCustomer,Marks a customer as inactive or removes them from the system.
createBankAccount,Opens a new bank account for a customer.
closeBankAccount,Closes an existing bank account.
getBankAccountDetails,Retrieves details of a specific bank account.
listCustomerAccounts,Lists all accounts associated with a customer.
updateAccountStatus,Changes the status of a bank account (e.g. active dormant frozen).
depositFunds,Adds funds to a specified bank account.
withdrawFunds,Removes funds from a specified bank account.
transferFunds,Moves funds between two accounts.
getAccountBalance,Retrieves the current balance of an account.
getAccountTransactions,Lists transactions for a specific account within a date range.
initiateWireTransfer,Starts a wire transfer process to an external account.
scheduleRecurringTransfer,Sets up a recurring transfer between accounts.
cancelRecurringTransfer,Cancels an existing recurring transfer.
getRealTimeExchangeRates,Fetches current exchange rates for international transfers.
estimateTransferFees,Calculates estimated fees for a potential transfer.
applyForLoan,Submits a loan application for a customer.
getLoanDetails,Retrieves details of a specific loan.
listCustomerLoans,Lists all loans associated with a customer.
calculateLoanEligibility,Determines a customer's eligibility for a loan.
getLoanRepaymentSchedule,Retrieves the repayment schedule for a loan.
makeLoanPayment,Processes a payment towards a loan.
requestLoanRefinancing,Initiates a loan refinancing process.
calculateLoanInterest,Calculates interest for a loan over a specified period.
getLoanStatements,Retrieves loan statements for a given period.
updateLoanTerms,Modifies the terms of an existing loan.
applyCreditCard,Submits a credit card application for a customer.
activateCreditCard,Activates a newly issued credit card.
getCreditCardDetails,Retrieves details of a specific credit card.
listCustomerCreditCards,Lists all credit cards associated with a customer.
reportLostCreditCard,Reports a credit card as lost or stolen.
getCreditCardTransactions,Lists transactions for a specific credit card within a date range.
makeCardPayment,Processes a payment towards a credit card balance.
adjustCreditLimit,Changes the credit limit on a card.
requestCashAdvance,Initiates a cash advance on a credit card.
disputeTransaction,Starts a dispute process for a specific transaction.
getCardRewards,Retrieves reward points or cashback information for a card.
redeemCardRewards,Processes a redemption of card rewards.
getCreditScore,Retrieves a customer's credit score.
setUpAutopay,Establishes automatic payments for a credit card.
getCreditCardStatement,Retrieves a credit card statement for a specific period.
createSavingsGoal,Sets up a new savings goal for a customer.
updateSavingsGoal,Modifies an existing savings goal.
trackSavingsProgress,Retrieves progress towards a savings goal.
listSavingsGoals,Lists all savings goals for a customer.
automateSavingsTransfer,Sets up automatic transfers to a savings goal.
openCertificateOfDeposit,Creates a new Certificate of Deposit account.
calculateCDMaturityAmount,Estimates the maturity amount for a CD.
closeCDAccount,Closes a Certificate of Deposit account.
listInvestmentOptions,Retrieves available investment products.
purchaseInvestmentProduct,Processes the purchase of an investment product.
sellInvestmentProduct,Processes the sale of an investment product.
getInvestmentPortfolio,Retrieves a customer's investment portfolio details.
calculateInvestmentReturns,Calculates returns on investments over a period.
rebalancePortfolio,Adjusts the allocation of investments in a portfolio.
getMarketInsights,Retrieves market analysis and insights.
setUpDirectDeposit,Establishes a direct deposit arrangement for an account.
issueCheckbook,Requests a new checkbook for an account.
stopCheckPayment,Places a stop payment on a specific check.
orderForeignCurrency,Initiates an order for foreign currency.
getNearestATMLocation,Finds the nearest ATM locations based on provided coordinates.
getNearestBranchLocation,Finds the nearest bank branch locations based on provided coordinates.
scheduleAppointment,Books an appointment with a bank representative.
updateContactPreferences,Updates a customer's contact preferences.
enableTwoFactorAuth,Enables two-factor authentication for a customer's online banking.
resetPassword,Initiates the process to reset a customer's password.
getAccountStatements,Retrieves account statements for a specified period.
downloadTaxDocuments,Retrieves tax-related documents for a customer.
updateBeneficiary,Updates beneficiary information for an account.
applyForMortgage,Submits a mortgage application.
getMortgageRates,Retrieves current mortgage rates.
calculateMortgagePayments,Estimates mortgage payments based on loan details.
refinanceMortgage,Initiates a mortgage refinancing process.
getPropertyValuation,Requests a property valuation for mortgage purposes.
setUpBillPay,Establishes a bill payment arrangement.
scheduleBillPayment,Schedules a one-time or recurring bill payment.
cancelBillPayment,Cancels a scheduled bill payment.
listPayees,Retrieves a list of registered payees for bill payments.
addPayee,Adds a new payee for bill payments.
removePayee,Removes a payee from the bill pay system.
getOverdraftStatus,Checks the overdraft status of an account.
enableOverdraftProtection,Enables overdraft protection for an account.
getLoanPayoffAmount,Calculates the payoff amount for a loan.
initiateChargebackRequest,Starts a chargeback process for a card transaction.
getFraudAlerts,Retrieves recent fraud alerts for a customer.
updateFraudAlertSettings,Modifies fraud alert settings for a customer.
getAccountAggregation,Retrieves aggregated financial information across all accounts.
linkExternalAccount,Links an external account for transfers or aggregation.
unlinkExternalAccount,Removes a linked external account.
getCashFlowAnalysis,Provides a cash flow analysis for a specified period.
getBudgetRecommendations,Generates budget recommendations based on spending patterns.
categorizeTransaction,Assigns a category to a specific transaction.
getSpendingInsights,Provides insights on spending patterns.
setSpendingLimit,Sets a spending limit on a card or account.
initiateDisputeResolution,Starts the dispute resolution process for an account issue.
getProductRecommendations,Provides personalized product recommendations based on customer profile.
        
Given the user question below, and the APIs above, classify and give a correct API name to call. 

The question could relate to 2 or more APIs, please enlist them with correct order.

Answer should be formatted, looks like [getCustomerDetails,depositFunds] or [getCustomerDetails].

<question>
{question}
</question>

Classification:"""
    )
    | llm
    | StrOutputParser()
)



# SQL Query 
write_query = create_sql_query_chain(llm, db)
sqlanswer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)
sqlanswer = sqlanswer_prompt | llm | StrOutputParser()
sqlchain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | sqlanswer
)



# Router
branch = RunnableBranch(
(lambda x: "1" in x["topic"].lower(), apicaller),
(lambda x: "2" in x["topic"].lower(), sqlchain),
llm,
)


# Router + Branch
# full_chain ={"topic": router_chain,"question":lambda x: x["question"],"template":lambda x: x["template"]}| branch



# print(full_chain.invoke({"question": "What is the account ID of the customer Sam?","template":template1}))
# print(full_chain.invoke({"question": "What is the balance of account LB00001 today?","template":template2}))
# print(chain.invoke({"question": "What are the type of cards available at BGL?"}))

# print(chain.invoke({"question": "Translate \"I am your father\" in French"}))

# print(full_chain.invoke({"question": "How much did the customer LB00001 paid last month"}))
# print(full_chain.invoke({"question": "Find the total amount of transactions made in 'EUR' currency."}))

# print(chain.invoke({"question": "Summarize the following context and translate it in English :\"Bonjour, comment ça va?\""}))
# print(chain.invoke({"question": "How much did the customer named Thomas paid in Germany?"}))
# print(chain.invoke({"question": "Provide a summary in English of the most recent transactions, payments, and current balance for the customer named 'Juan Pérez'. Additionally, retrieve any common questions or documents related to this customer's transactions and include the translated answers to those questions if they are in a different language."}))


print(router_chain.invoke({"question":"How often should the exchange rates be updated to ensure accuracy in international transfers?"}))


print(router_chain.invoke({"question":"Create a customer named Sam and submit a credit card application for him."}))


print(router_chain.invoke({"question":"Create a customer named Sam, make an appointment tomorrow 14h00, set his saving goal as $10000 and get his credit score then submit a credit card application."}))
