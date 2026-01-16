'use client';

import { useState } from 'react';
import type {
  LoanScenario,
  LoanFormData,
  FormErrors,
  PropertyType,
  Occupancy,
  LoanTerm,
} from '@/lib/types';
import {
  US_STATES,
  PROPERTY_TYPES,
  OCCUPANCY_TYPES,
  LOAN_TERMS,
} from '@/lib/types';

interface LoanFormProps {
  onSubmit: (scenario: LoanScenario) => void;
  isLoading?: boolean;
}

const initialFormData: LoanFormData = {
  credit_score: '',
  annual_income: '',
  is_first_time_buyer: true,
  loan_amount: '',
  property_value: '',
  loan_term_years: 30,
  monthly_debt_payments: '',
  property_type: 'single_family',
  property_state: '',
  property_county: '',
  occupancy: 'primary',
};

function formatCurrency(value: string): string {
  // Remove non-numeric characters except decimal point
  const numericValue = value.replace(/[^0-9.]/g, '');
  if (!numericValue) return '';

  const number = parseFloat(numericValue);
  if (isNaN(number)) return '';

  return number.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

function parseCurrency(value: string): number {
  return parseFloat(value.replace(/[^0-9.]/g, '')) || 0;
}

export default function LoanForm({ onSubmit, isLoading = false }: LoanFormProps) {
  const [formData, setFormData] = useState<LoanFormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateField = (name: string, value: string | number | boolean): string | undefined => {
    switch (name) {
      case 'credit_score': {
        const score = typeof value === 'string' ? parseInt(value, 10) : value;
        if (!value || isNaN(score as number)) return 'Credit score is required';
        if ((score as number) < 300 || (score as number) > 850) return 'Credit score must be between 300 and 850';
        return undefined;
      }
      case 'annual_income': {
        const income = parseCurrency(value as string);
        if (!value || income <= 0) return 'Annual income is required';
        if (income < 10000) return 'Annual income seems too low';
        if (income > 10000000) return 'Annual income seems too high';
        return undefined;
      }
      case 'loan_amount': {
        const amount = parseCurrency(value as string);
        if (!value || amount <= 0) return 'Loan amount is required';
        if (amount < 10000) return 'Loan amount must be at least $10,000';
        if (amount > 5000000) return 'Loan amount exceeds program limits';
        return undefined;
      }
      case 'property_value': {
        const pValue = parseCurrency(value as string);
        if (!value || pValue <= 0) return 'Property value is required';
        if (pValue < 20000) return 'Property value seems too low';
        return undefined;
      }
      case 'monthly_debt_payments': {
        const debt = parseCurrency(value as string);
        if (value && debt < 0) return 'Monthly debt cannot be negative';
        return undefined;
      }
      case 'property_state':
        if (!value) return 'State is required';
        return undefined;
      case 'property_county':
        if (!value) return 'County is required';
        return undefined;
      default:
        return undefined;
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;

    // Validate all fields
    Object.entries(formData).forEach(([key, value]) => {
      const error = validateField(key, value);
      if (error) {
        newErrors[key] = error;
        isValid = false;
      }
    });

    // Additional validation: loan amount vs property value
    const loanAmount = parseCurrency(formData.loan_amount);
    const propertyValue = parseCurrency(formData.property_value);
    if (loanAmount > 0 && propertyValue > 0) {
      const ltv = loanAmount / propertyValue;
      if (ltv > 0.97) {
        newErrors.loan_amount = 'Loan amount cannot exceed 97% of property value';
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    let newValue: string | boolean | number = value;

    if (type === 'checkbox') {
      newValue = (e.target as HTMLInputElement).checked;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleCurrencyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const formatted = formatCurrency(value);
    setFormData((prev) => ({
      ...prev,
      [name]: formatted,
    }));

    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    const error = validateField(name, value);
    if (error) {
      setErrors((prev) => ({ ...prev, [name]: error }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Mark all fields as touched
    const allTouched: Record<string, boolean> = {};
    Object.keys(formData).forEach((key) => {
      allTouched[key] = true;
    });
    setTouched(allTouched);

    if (!validateForm()) {
      return;
    }

    // Convert form data to LoanScenario
    const scenario: LoanScenario = {
      credit_score: parseInt(formData.credit_score, 10),
      annual_income: parseCurrency(formData.annual_income),
      is_first_time_buyer: formData.is_first_time_buyer,
      loan_amount: parseCurrency(formData.loan_amount),
      property_value: parseCurrency(formData.property_value),
      loan_term_years: formData.loan_term_years,
      monthly_debt_payments: parseCurrency(formData.monthly_debt_payments) || 0,
      property_type: formData.property_type,
      property_state: formData.property_state,
      property_county: formData.property_county,
      occupancy: formData.occupancy,
    };

    onSubmit(scenario);
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setErrors({});
    setTouched({});
  };

  // Calculate LTV preview
  const loanAmount = parseCurrency(formData.loan_amount);
  const propertyValue = parseCurrency(formData.property_value);
  const ltvPreview = loanAmount > 0 && propertyValue > 0
    ? ((loanAmount / propertyValue) * 100).toFixed(1)
    : null;

  // Calculate estimated DTI preview
  const annualIncome = parseCurrency(formData.annual_income);
  const monthlyDebt = parseCurrency(formData.monthly_debt_payments) || 0;
  const monthlyIncome = annualIncome / 12;
  const estimatedMonthlyPayment = loanAmount * 0.006; // Rough estimate
  const dtiPreview = monthlyIncome > 0
    ? (((monthlyDebt + estimatedMonthlyPayment) / monthlyIncome) * 100).toFixed(1)
    : null;

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {/* Borrower Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Borrower Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Credit Score */}
          <div>
            <label
              htmlFor="credit_score"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Credit Score *
            </label>
            <input
              type="number"
              id="credit_score"
              name="credit_score"
              value={formData.credit_score}
              onChange={handleChange}
              onBlur={handleBlur}
              min="300"
              max="850"
              placeholder="620"
              className={`
                w-full px-4 py-2 rounded-lg border
                focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                ${errors.credit_score && touched.credit_score
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-300'
                }
              `}
            />
            {errors.credit_score && touched.credit_score && (
              <p className="mt-1 text-sm text-red-600">{errors.credit_score}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              HomeReady: 620+ | Home Possible: 660+
            </p>
          </div>

          {/* Annual Income */}
          <div>
            <label
              htmlFor="annual_income"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Annual Income *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="text"
                id="annual_income"
                name="annual_income"
                value={formData.annual_income}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="75,000"
                className={`
                  w-full pl-8 pr-4 py-2 rounded-lg border
                  focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                  ${errors.annual_income && touched.annual_income
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                  }
                `}
              />
            </div>
            {errors.annual_income && touched.annual_income && (
              <p className="mt-1 text-sm text-red-600">{errors.annual_income}</p>
            )}
          </div>

          {/* First Time Buyer */}
          <div className="md:col-span-2">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                name="is_first_time_buyer"
                checked={formData.is_first_time_buyer}
                onChange={handleChange}
                className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <span className="text-sm font-medium text-gray-700">
                First-time homebuyer
              </span>
            </label>
            <p className="mt-1 ml-8 text-xs text-gray-500">
              Homeownership education may be required for first-time buyers
            </p>
          </div>
        </div>
      </div>

      {/* Loan Details */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Loan Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Loan Amount */}
          <div>
            <label
              htmlFor="loan_amount"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Loan Amount *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="text"
                id="loan_amount"
                name="loan_amount"
                value={formData.loan_amount}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="350,000"
                className={`
                  w-full pl-8 pr-4 py-2 rounded-lg border
                  focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                  ${errors.loan_amount && touched.loan_amount
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                  }
                `}
              />
            </div>
            {errors.loan_amount && touched.loan_amount && (
              <p className="mt-1 text-sm text-red-600">{errors.loan_amount}</p>
            )}
          </div>

          {/* Property Value */}
          <div>
            <label
              htmlFor="property_value"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Property Value *
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="text"
                id="property_value"
                name="property_value"
                value={formData.property_value}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="400,000"
                className={`
                  w-full pl-8 pr-4 py-2 rounded-lg border
                  focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                  ${errors.property_value && touched.property_value
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                  }
                `}
              />
            </div>
            {errors.property_value && touched.property_value && (
              <p className="mt-1 text-sm text-red-600">{errors.property_value}</p>
            )}
          </div>

          {/* Loan Term */}
          <div>
            <label
              htmlFor="loan_term_years"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Loan Term
            </label>
            <select
              id="loan_term_years"
              name="loan_term_years"
              value={formData.loan_term_years}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  loan_term_years: parseInt(e.target.value, 10) as LoanTerm,
                }))
              }
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {LOAN_TERMS.map((term) => (
                <option key={term.value} value={term.value}>
                  {term.label}
                </option>
              ))}
            </select>
          </div>

          {/* Monthly Debt Payments */}
          <div>
            <label
              htmlFor="monthly_debt_payments"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Monthly Debt Payments
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">$</span>
              <input
                type="text"
                id="monthly_debt_payments"
                name="monthly_debt_payments"
                value={formData.monthly_debt_payments}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="500"
                className={`
                  w-full pl-8 pr-4 py-2 rounded-lg border
                  focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                  ${errors.monthly_debt_payments && touched.monthly_debt_payments
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-300'
                  }
                `}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Car loans, student loans, credit cards, etc.
            </p>
          </div>

          {/* LTV & DTI Preview */}
          <div className="md:col-span-2 lg:col-span-2">
            <div className="bg-gray-50 rounded-lg p-4 flex space-x-8">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Estimated LTV
                </p>
                <p className={`text-2xl font-semibold ${
                  ltvPreview && parseFloat(ltvPreview) > 97
                    ? 'text-red-600'
                    : ltvPreview && parseFloat(ltvPreview) > 95
                    ? 'text-amber-600'
                    : 'text-gray-900'
                }`}>
                  {ltvPreview ? `${ltvPreview}%` : '--'}
                </p>
                <p className="text-xs text-gray-500">Max: 97%</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide">
                  Estimated DTI
                </p>
                <p className={`text-2xl font-semibold ${
                  dtiPreview && parseFloat(dtiPreview) > 50
                    ? 'text-red-600'
                    : dtiPreview && parseFloat(dtiPreview) > 45
                    ? 'text-amber-600'
                    : 'text-gray-900'
                }`}>
                  {dtiPreview ? `${dtiPreview}%` : '--'}
                </p>
                <p className="text-xs text-gray-500">Max: 45-50%</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Property Information */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Property Information
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Property Type */}
          <div>
            <label
              htmlFor="property_type"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Property Type
            </label>
            <select
              id="property_type"
              name="property_type"
              value={formData.property_type}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  property_type: e.target.value as PropertyType,
                }))
              }
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {PROPERTY_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Occupancy */}
          <div>
            <label
              htmlFor="occupancy"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Occupancy Type
            </label>
            <select
              id="occupancy"
              name="occupancy"
              value={formData.occupancy}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  occupancy: e.target.value as Occupancy,
                }))
              }
              className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {OCCUPANCY_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {formData.occupancy !== 'primary' && (
              <p className="mt-1 text-xs text-amber-600">
                Note: HomeReady and Home Possible require primary residence
              </p>
            )}
          </div>

          {/* State */}
          <div>
            <label
              htmlFor="property_state"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              State *
            </label>
            <select
              id="property_state"
              name="property_state"
              value={formData.property_state}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`
                w-full px-4 py-2 rounded-lg border
                focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                ${errors.property_state && touched.property_state
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-300'
                }
              `}
            >
              <option value="">Select a state</option>
              {US_STATES.map((state) => (
                <option key={state.code} value={state.code}>
                  {state.name}
                </option>
              ))}
            </select>
            {errors.property_state && touched.property_state && (
              <p className="mt-1 text-sm text-red-600">{errors.property_state}</p>
            )}
          </div>

          {/* County */}
          <div>
            <label
              htmlFor="property_county"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              County *
            </label>
            <input
              type="text"
              id="property_county"
              name="property_county"
              value={formData.property_county}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Los Angeles"
              className={`
                w-full px-4 py-2 rounded-lg border
                focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                ${errors.property_county && touched.property_county
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-300'
                }
              `}
            />
            {errors.property_county && touched.property_county && (
              <p className="mt-1 text-sm text-red-600">{errors.property_county}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Used for income limits and loan limits
            </p>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          type="submit"
          disabled={isLoading}
          className={`
            flex-1 px-6 py-3 rounded-lg font-semibold text-white
            transition-colors duration-150
            ${isLoading
              ? 'bg-indigo-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800'
            }
          `}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Checking Eligibility...
            </span>
          ) : (
            'Check Eligibility'
          )}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="px-6 py-3 rounded-lg font-semibold text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-colors duration-150"
        >
          Reset Form
        </button>
      </div>
    </form>
  );
}
