export interface CreditCard {
  id: string;
  card_name: string;
  issuer: string;
  network: string;
  card_type: string;
  annual_fees: number;
  apr_information: string;
  transaction_fees: number;
  credit_score_requirements: string;
  welcome_bonus_details?: string;
  regular_rewards_rates: number;
  category_specific_reward_rates: Record<string, any>;
  travel_benefits?: string;
  shopping_perks?: string;
  insurance_coverage?: string;
  affiliate_links?: string;
  commission_rates?: number;
  tracking_ids?: string;
  card_images?: string;
  logos?: string;
  meta_information?: Record<string, any>;
  active_status: boolean;
  featured_ranking?: number;
  popularity_metrics?: number;
}

export interface CreditCardFormData extends Omit<CreditCard, 'id'> {} 