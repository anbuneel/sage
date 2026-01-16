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
import {
  User,
  CurrencyDollar,
  House,
  CaretDown,
  CircleNotch,
  ArrowCounterClockwise,
  CheckCircle,
  Warning,
} from '@phosphor-icons/react';

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

    Object.entries(formData).forEach(([key, value]) => {
      const error = validateField(key, value);
      if (error) {
        newErrors[key] = error;
        isValid = false;
      }
    });

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

    const allTouched: Record<string, boolean> = {};
    Object.keys(formData).forEach((key) => {
      allTouched[key] = true;
    });
    setTouched(allTouched);

    if (!validateForm()) {
      return;
    }

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
  const estimatedMonthlyPayment = loanAmount * 0.006;
  const dtiPreview = monthlyIncome > 0
    ? (((monthlyDebt + estimatedMonthlyPayment) / monthlyIncome) * 100).toFixed(1)
    : null;

  const getLtvColor = (ltv: string | null) => {
    if (!ltv) return 'text-ink-500';
    const value = parseFloat(ltv);
    if (value > 97) return 'text-error';
    if (value > 95) return 'text-gold-600';
    return 'text-success';
  };

  const getDtiColor = (dti: string | null) => {
    if (!dti) return 'text-ink-500';
    const value = parseFloat(dti);
    if (value > 50) return 'text-error';
    if (value > 45) return 'text-gold-600';
    return 'text-success';
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-10">
      {/* Borrower Information */}
      <fieldset className="bg-surface border border-border p-6 md:p-8 relative">
        <div className="absolute top-0 left-6 -translate-y-1/2 bg-surface px-3 py-1 flex items-center gap-2">
          <User size={20} weight="thin" className="text-sage-600" />
          <span className="font-display text-lg font-semibold text-ink-900">
            Borrower Information
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mt-4">
          {/* Credit Score */}
          <div>
            <label htmlFor="credit_score" className="block text-sm font-medium text-ink-700 mb-2">
              Credit Score <span className="text-error">*</span>
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
              className={`input input-mono ${
                errors.credit_score && touched.credit_score
                  ? 'border-error/50 bg-error/5'
                  : ''
              }`}
            />
            {errors.credit_score && touched.credit_score && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.credit_score}
              </p>
            )}
            <p className="mt-1 text-xs text-ink-500">
              HomeReady: 620+ | Home Possible: 660+
            </p>
          </div>

          {/* Annual Income */}
          <div>
            <label htmlFor="annual_income" className="block text-sm font-medium text-ink-700 mb-2">
              Annual Income <span className="text-error">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-500 font-mono">$</span>
              <input
                type="text"
                id="annual_income"
                name="annual_income"
                value={formData.annual_income}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="75,000"
                className={`input input-mono pl-8 ${
                  errors.annual_income && touched.annual_income
                    ? 'border-error/50 bg-error/5'
                    : ''
                }`}
              />
            </div>
            {errors.annual_income && touched.annual_income && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.annual_income}
              </p>
            )}
          </div>

          {/* First Time Buyer */}
          <div className="md:col-span-2">
            <label className="flex items-center gap-3 cursor-pointer group">
              <div className="relative">
                <input
                  type="checkbox"
                  name="is_first_time_buyer"
                  checked={formData.is_first_time_buyer}
                  onChange={handleChange}
                  className="sr-only peer"
                />
                <div className="w-5 h-5 border border-border bg-white peer-checked:bg-sage-600 peer-checked:border-sage-600 peer-focus:ring-2 peer-focus:ring-sage-600/20 transition-colors">
                  {formData.is_first_time_buyer && (
                    <CheckCircle size={18} weight="bold" className="text-white m-px" />
                  )}
                </div>
              </div>
              <span className="text-sm font-medium text-ink-700 group-hover:text-ink-900">
                First-time homebuyer
              </span>
            </label>
            <p className="mt-1 ml-8 text-xs text-ink-500">
              Homeownership education may be required for first-time buyers
            </p>
          </div>
        </div>
      </fieldset>

      {/* Loan Details */}
      <fieldset className="bg-surface border border-border p-6 md:p-8 relative">
        <div className="absolute top-0 left-6 -translate-y-1/2 bg-surface px-3 py-1 flex items-center gap-2">
          <CurrencyDollar size={20} weight="thin" className="text-sage-600" />
          <span className="font-display text-lg font-semibold text-ink-900">
            Loan Details
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 mt-4">
          {/* Loan Amount */}
          <div>
            <label htmlFor="loan_amount" className="block text-sm font-medium text-ink-700 mb-2">
              Loan Amount <span className="text-error">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-500 font-mono">$</span>
              <input
                type="text"
                id="loan_amount"
                name="loan_amount"
                value={formData.loan_amount}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="350,000"
                className={`input input-mono pl-8 ${
                  errors.loan_amount && touched.loan_amount
                    ? 'border-error/50 bg-error/5'
                    : ''
                }`}
              />
            </div>
            {errors.loan_amount && touched.loan_amount && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.loan_amount}
              </p>
            )}
          </div>

          {/* Property Value */}
          <div>
            <label htmlFor="property_value" className="block text-sm font-medium text-ink-700 mb-2">
              Property Value <span className="text-error">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-500 font-mono">$</span>
              <input
                type="text"
                id="property_value"
                name="property_value"
                value={formData.property_value}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="400,000"
                className={`input input-mono pl-8 ${
                  errors.property_value && touched.property_value
                    ? 'border-error/50 bg-error/5'
                    : ''
                }`}
              />
            </div>
            {errors.property_value && touched.property_value && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.property_value}
              </p>
            )}
          </div>

          {/* Loan Term */}
          <div>
            <label htmlFor="loan_term_years" className="block text-sm font-medium text-ink-700 mb-2">
              Loan Term
            </label>
            <div className="relative">
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
                className="select appearance-none pr-10"
              >
                {LOAN_TERMS.map((term) => (
                  <option key={term.value} value={term.value}>
                    {term.label}
                  </option>
                ))}
              </select>
              <CaretDown
                size={16}
                weight="thin"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-ink-500 pointer-events-none"
              />
            </div>
          </div>

          {/* Monthly Debt Payments */}
          <div>
            <label htmlFor="monthly_debt_payments" className="block text-sm font-medium text-ink-700 mb-2">
              Monthly Debt Payments
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-500 font-mono">$</span>
              <input
                type="text"
                id="monthly_debt_payments"
                name="monthly_debt_payments"
                value={formData.monthly_debt_payments}
                onChange={handleCurrencyChange}
                onBlur={handleBlur}
                placeholder="500"
                className={`input input-mono pl-8 ${
                  errors.monthly_debt_payments && touched.monthly_debt_payments
                    ? 'border-error/50 bg-error/5'
                    : ''
                }`}
              />
            </div>
            <p className="mt-1 text-xs text-ink-500">
              Car loans, student loans, credit cards, etc.
            </p>
          </div>

          {/* LTV & DTI Preview */}
          <div className="md:col-span-2 lg:col-span-2">
            <div className="bg-paper border-2 border-border p-6 flex gap-12">
              <div>
                <p className="text-xs font-mono uppercase tracking-wider text-ink-500 mb-2">
                  Estimated LTV
                </p>
                <p className={`text-3xl font-mono font-semibold ${getLtvColor(ltvPreview)}`}>
                  {ltvPreview ? `${ltvPreview}%` : '--'}
                </p>
                <p className="text-xs text-ink-500 mt-2">Max: 97%</p>
              </div>
              <div className="w-px bg-border" />
              <div>
                <p className="text-xs font-mono uppercase tracking-wider text-ink-500 mb-2">
                  Estimated DTI
                </p>
                <p className={`text-3xl font-mono font-semibold ${getDtiColor(dtiPreview)}`}>
                  {dtiPreview ? `${dtiPreview}%` : '--'}
                </p>
                <p className="text-xs text-ink-500 mt-2">Max: 45-50%</p>
              </div>
            </div>
          </div>
        </div>
      </fieldset>

      {/* Property Information */}
      <fieldset className="bg-surface border border-border p-6 md:p-8 relative">
        <div className="absolute top-0 left-6 -translate-y-1/2 bg-surface px-3 py-1 flex items-center gap-2">
          <House size={20} weight="thin" className="text-sage-600" />
          <span className="font-display text-lg font-semibold text-ink-900">
            Property Information
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 mt-4">
          {/* Property Type */}
          <div>
            <label htmlFor="property_type" className="block text-sm font-medium text-ink-700 mb-2">
              Property Type
            </label>
            <div className="relative">
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
                className="select appearance-none pr-10"
              >
                {PROPERTY_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <CaretDown
                size={16}
                weight="thin"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-ink-500 pointer-events-none"
              />
            </div>
          </div>

          {/* Occupancy */}
          <div>
            <label htmlFor="occupancy" className="block text-sm font-medium text-ink-700 mb-2">
              Occupancy Type
            </label>
            <div className="relative">
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
                className="select appearance-none pr-10"
              >
                {OCCUPANCY_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
              <CaretDown
                size={16}
                weight="thin"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-ink-500 pointer-events-none"
              />
            </div>
            {formData.occupancy !== 'primary' && (
              <p className="mt-1 text-xs text-gold-600 flex items-center gap-1">
                <Warning size={12} weight="thin" />
                HomeReady and Home Possible require primary residence
              </p>
            )}
          </div>

          {/* State */}
          <div>
            <label htmlFor="property_state" className="block text-sm font-medium text-ink-700 mb-2">
              State <span className="text-error">*</span>
            </label>
            <div className="relative">
              <select
                id="property_state"
                name="property_state"
                value={formData.property_state}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`select appearance-none pr-10 ${
                  errors.property_state && touched.property_state
                    ? 'border-error/50 bg-error/5'
                    : ''
                }`}
              >
                <option value="">Select a state</option>
                {US_STATES.map((state) => (
                  <option key={state.code} value={state.code}>
                    {state.name}
                  </option>
                ))}
              </select>
              <CaretDown
                size={16}
                weight="thin"
                className="absolute right-4 top-1/2 -translate-y-1/2 text-ink-500 pointer-events-none"
              />
            </div>
            {errors.property_state && touched.property_state && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.property_state}
              </p>
            )}
          </div>

          {/* County */}
          <div>
            <label htmlFor="property_county" className="block text-sm font-medium text-ink-700 mb-2">
              County <span className="text-error">*</span>
            </label>
            <input
              type="text"
              id="property_county"
              name="property_county"
              value={formData.property_county}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Los Angeles"
              className={`input ${
                errors.property_county && touched.property_county
                  ? 'border-error/50 bg-error/5'
                  : ''
              }`}
            />
            {errors.property_county && touched.property_county && (
              <p className="mt-1 text-sm text-error flex items-center gap-1">
                <Warning size={14} weight="thin" />
                {errors.property_county}
              </p>
            )}
            <p className="mt-1 text-xs text-ink-500">
              Used for income limits and loan limits
            </p>
          </div>
        </div>
      </fieldset>

      {/* Form Actions */}
      <div className="flex flex-col sm:flex-row gap-4 pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className={`btn btn-primary btn-lg flex-1 inline-flex items-center justify-center gap-3 ${
            isLoading ? 'opacity-60 cursor-not-allowed' : ''
          }`}
        >
          {isLoading ? (
            <>
              <CircleNotch size={20} weight="bold" className="animate-spin" />
              Checking Eligibility...
            </>
          ) : (
            <>
              <CheckCircle size={20} weight="bold" />
              Check Eligibility
            </>
          )}
        </button>
        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="btn btn-secondary btn-lg inline-flex items-center justify-center gap-2"
        >
          <ArrowCounterClockwise size={20} weight="thin" />
          Reset Form
        </button>
      </div>
    </form>
  );
}
