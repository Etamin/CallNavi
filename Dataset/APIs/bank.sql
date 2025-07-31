-- Customers
CREATE TABLE Customers (
  customer_id TEXT PRIMARY KEY,
  name TEXT,
  email TEXT,
  phone TEXT,
  address TEXT
);

-- Accounts
CREATE TABLE Accounts (
  account_id TEXT PRIMARY KEY,
  customer_id TEXT,
  name TEXT,
  type TEXT,
  balance REAL,
  currency TEXT,
  overdraft_limit REAL,
  branch_id TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
  FOREIGN KEY(branch_id) REFERENCES Branches(branch_id)
);

-- Transactions
CREATE TABLE Transactions (
  transaction_id TEXT PRIMARY KEY,
  account_id TEXT,
  type TEXT,
  amount REAL,
  currency TEXT,
  timestamp TEXT,
  description TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

-- Funds Transfers
CREATE TABLE Transfers (
  transfer_id TEXT PRIMARY KEY,
  from_account_id TEXT,
  to_account_id TEXT,
  amount REAL,
  currency TEXT,
  status TEXT,
  initiated_at TEXT,
  FOREIGN KEY(from_account_id) REFERENCES Accounts(account_id),
  FOREIGN KEY(to_account_id) REFERENCES Accounts(account_id)
);

-- Wire Transfers
CREATE TABLE WireTransfers (
  transfer_id TEXT PRIMARY KEY,
  from_account_id TEXT,
  to_bank_details TEXT,
  amount REAL,
  currency TEXT,
  status TEXT,
  initiated_at TEXT,
  FOREIGN KEY(from_account_id) REFERENCES Accounts(account_id)
);

-- Recurring Payments
CREATE TABLE RecurringPayments (
  recurring_payment_id TEXT PRIMARY KEY,
  from_account_id TEXT,
  to_account_id TEXT,
  amount REAL,
  currency TEXT,
  frequency TEXT,
  status TEXT,
  created_at TEXT,
  last_executed TEXT,
  FOREIGN KEY(from_account_id) REFERENCES Accounts(account_id),
  FOREIGN KEY(to_account_id) REFERENCES Accounts(account_id)
);

-- Loans and Payments
CREATE TABLE Loans (
  loan_id TEXT PRIMARY KEY,
  customer_id TEXT,
  loan_type TEXT,
  original_amount REAL,
  outstanding_balance REAL,
  status TEXT,
  application_date TEXT,
  term_length INTEGER,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE LoanPayments (
  payment_id TEXT PRIMARY KEY,
  loan_id TEXT,
  amount REAL,
  payment_method TEXT,
  payment_date TEXT,
  FOREIGN KEY(loan_id) REFERENCES Loans(loan_id)
);

-- Mortgages and Payments
CREATE TABLE Mortgages (
  mortgage_id TEXT PRIMARY KEY,
  customer_id TEXT,
  property_value REAL,
  loan_amount REAL,
  outstanding_balance REAL,
  term_length INTEGER,
  status TEXT,
  application_date TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE MortgagePayments (
  payment_id TEXT PRIMARY KEY,
  mortgage_id TEXT,
  amount REAL,
  payment_method TEXT,
  payment_date TEXT,
  FOREIGN KEY(mortgage_id) REFERENCES Mortgages(mortgage_id)
);

-- Overdrafts
CREATE TABLE Overdrafts (
  overdraft_id TEXT PRIMARY KEY,
  account_id TEXT,
  limit REAL,
  status TEXT,
  applied_at TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

-- ATM Cards
CREATE TABLE ATMCards (
  card_id TEXT PRIMARY KEY,
  account_id TEXT,
  card_number TEXT,
  expiry_date TEXT,
  status TEXT,
  pin TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

-- Credit Cards and Payments
CREATE TABLE CreditCards (
  card_id TEXT PRIMARY KEY,
  account_id TEXT,
  credit_card_number TEXT,
  expiry_date TEXT,
  cvv TEXT,
  status TEXT,
  credit_limit REAL,
  outstanding_balance REAL,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

CREATE TABLE CreditCardPayments (
  payment_id TEXT PRIMARY KEY,
  credit_card_number TEXT,
  amount REAL,
  payment_method TEXT,
  payment_date TEXT
);

-- Statements
CREATE TABLE Statements (
  statement_id TEXT PRIMARY KEY,
  account_id TEXT,
  period_start TEXT,
  period_end TEXT,
  url TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

-- Branches and ATMs
CREATE TABLE Branches (
  branch_id TEXT PRIMARY KEY,
  name TEXT,
  address TEXT,
  location TEXT
);

CREATE TABLE BranchHours (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  branch_id TEXT,
  day_of_week TEXT,
  open_time TEXT,
  close_time TEXT,
  FOREIGN KEY(branch_id) REFERENCES Branches(branch_id)
);

CREATE TABLE ATMs (
  atm_id TEXT PRIMARY KEY,
  location TEXT,
  branch_id TEXT,
  status TEXT,
  FOREIGN KEY(branch_id) REFERENCES Branches(branch_id)
);

-- Currency & Interest Rates
CREATE TABLE CurrencyExchangeRates (
  currency_pair TEXT PRIMARY KEY,
  rates_json TEXT,
  last_updated TEXT
);

CREATE TABLE InterestRates (
  currency TEXT,
  term_length TEXT,
  rate REAL,
  PRIMARY KEY (currency, term_length)
);

-- Fixed & Recurring Deposits
CREATE TABLE FixedDeposits (
  fixed_deposit_id TEXT PRIMARY KEY,
  account_id TEXT,
  deposit_amount REAL,
  term_length INTEGER,
  interest_rate REAL,
  opened_at TEXT,
  status TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

CREATE TABLE RecurringDepositAccounts (
  recurring_deposit_id TEXT PRIMARY KEY,
  customer_id TEXT,
  monthly_installment REAL,
  term_length INTEGER,
  interest_rate REAL,
  opened_at TEXT,
  status TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

-- Investments & Transactions
CREATE TABLE Investments (
  investment_id TEXT PRIMARY KEY,
  customer_id TEXT,
  type TEXT,
  details_json TEXT,
  created_at TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE InvestmentTransactions (
  transaction_id TEXT PRIMARY KEY,
  investment_id TEXT,
  type TEXT,
  amount REAL,
  date TEXT,
  FOREIGN KEY(investment_id) REFERENCES Investments(investment_id)
);

-- Insurance Policies & Claims
CREATE TABLE InsurancePolicies (
  policy_id TEXT PRIMARY KEY,
  customer_id TEXT,
  policy_type TEXT,
  coverage_amount REAL,
  status TEXT,
  start_date TEXT,
  end_date TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE InsuranceClaims (
  claim_id TEXT PRIMARY KEY,
  policy_id TEXT,
  details_json TEXT,
  status TEXT,
  filed_at TEXT,
  FOREIGN KEY(policy_id) REFERENCES InsurancePolicies(policy_id)
);

CREATE TABLE InsurancePremiumPayments (
  payment_id TEXT PRIMARY KEY,
  policy_id TEXT,
  amount REAL,
  payment_method TEXT,
  payment_date TEXT,
  FOREIGN KEY(policy_id) REFERENCES InsurancePolicies(policy_id)
);

-- Recurring Alerts & Notifications
CREATE TABLE AccountAlerts (
  alert_id TEXT PRIMARY KEY,
  account_id TEXT,
  details_json TEXT,
  status TEXT,
  created_at TEXT,
  FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
);

CREATE TABLE CustomerNotifications (
  notification_id TEXT PRIMARY KEY,
  customer_id TEXT,
  details_json TEXT,
  status TEXT,
  created_at TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

-- Beneficiaries
CREATE TABLE Beneficiaries (
  beneficiary_id TEXT PRIMARY KEY,
  customer_id TEXT,
  details_json TEXT,
  added_at TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

-- Documents
CREATE TABLE CustomerDocuments (
  document_id TEXT PRIMARY KEY,
  customer_id TEXT,
  filename TEXT,
  url TEXT,
  uploaded_at TEXT,
  FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);
