# -*- coding: utf-8 -*-
import sys, os, certifi
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
os.environ['SSL_CERT_FILE'] = certifi.where()
import pandas as pd
base_url = pd.read_csv(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))) + "/Spot_trading/config.csv")['client'][0]

from Spot_trading.api import API

class Spot(API):
    def __init__(self, key=None, secret=None, **kwargs):
        if "base_url" not in kwargs:
            kwargs["base_url"] = base_url
        super().__init__(key, secret, **kwargs)

    # MARKETS
    from Spot_trading.spot.market import ping
    from Spot_trading.spot.market import time
    from Spot_trading.spot.market import exchange_info
    from Spot_trading.spot.market import depth
    from Spot_trading.spot.market import trades
    from Spot_trading.spot.market import historical_trades
    from Spot_trading.spot.market import agg_trades
    from Spot_trading.spot.market import klines
    from Spot_trading.spot.market import ui_klines
    from Spot_trading.spot.market import avg_price
    from Spot_trading.spot.market import ticker_24hr
    from Spot_trading.spot.market import ticker_price
    from Spot_trading.spot.market import book_ticker
    from Spot_trading.spot.market import rolling_window_ticker

    # ACCOUNT (including orders and trades)
    from Spot_trading.spot.trade import new_order_test
    from Spot_trading.spot.trade import new_order
    from Spot_trading.spot.trade import cancel_order
    from Spot_trading.spot.trade import cancel_open_orders
    from Spot_trading.spot.trade import get_order
    from Spot_trading.spot.trade import cancel_and_replace
    from Spot_trading.spot.trade import get_open_orders
    from Spot_trading.spot.trade import get_orders
    from Spot_trading.spot.trade import new_oco_order
    from Spot_trading.spot.trade import cancel_oco_order
    from Spot_trading.spot.trade import get_oco_order
    from Spot_trading.spot.trade import get_oco_orders
    from Spot_trading.spot.trade import get_oco_open_orders
    from Spot_trading.spot.trade import account
    from Spot_trading.spot.trade import my_trades
    from Spot_trading.spot.trade import get_order_rate_limit

    # STREAMS
    from Spot_trading.spot.data_stream import new_listen_key
    from Spot_trading.spot.data_stream import renew_listen_key
    from Spot_trading.spot.data_stream import close_listen_key
    from Spot_trading.spot.data_stream import new_margin_listen_key
    from Spot_trading.spot.data_stream import renew_margin_listen_key
    from Spot_trading.spot.data_stream import close_margin_listen_key
    from Spot_trading.spot.data_stream import new_isolated_margin_listen_key
    from Spot_trading.spot.data_stream import renew_isolated_margin_listen_key
    from Spot_trading.spot.data_stream import close_isolated_margin_listen_key

    # MARGIN
    from Spot_trading.spot.margin import margin_transfer
    from Spot_trading.spot.margin import margin_borrow
    from Spot_trading.spot.margin import margin_repay
    from Spot_trading.spot.margin import margin_asset
    from Spot_trading.spot.margin import margin_pair
    from Spot_trading.spot.margin import margin_all_assets
    from Spot_trading.spot.margin import margin_all_pairs
    from Spot_trading.spot.margin import margin_pair_index
    from Spot_trading.spot.margin import new_margin_order
    from Spot_trading.spot.margin import cancel_margin_order
    from Spot_trading.spot.margin import margin_transfer_history
    from Spot_trading.spot.margin import margin_load_record
    from Spot_trading.spot.margin import margin_repay_record
    from Spot_trading.spot.margin import margin_interest_history
    from Spot_trading.spot.margin import margin_force_liquidation_record
    from Spot_trading.spot.margin import margin_account
    from Spot_trading.spot.margin import margin_order
    from Spot_trading.spot.margin import margin_open_orders
    from Spot_trading.spot.margin import margin_open_orders_cancellation
    from Spot_trading.spot.margin import margin_all_orders
    from Spot_trading.spot.margin import margin_my_trades
    from Spot_trading.spot.margin import margin_max_borrowable
    from Spot_trading.spot.margin import margin_max_transferable
    from Spot_trading.spot.margin import isolated_margin_transfer
    from Spot_trading.spot.margin import isolated_margin_transfer_history
    from Spot_trading.spot.margin import isolated_margin_account
    from Spot_trading.spot.margin import isolated_margin_pair
    from Spot_trading.spot.margin import isolated_margin_all_pairs
    from Spot_trading.spot.margin import toggle_bnbBurn
    from Spot_trading.spot.margin import bnbBurn_status
    from Spot_trading.spot.margin import margin_interest_rate_history
    from Spot_trading.spot.margin import new_margin_oco_order
    from Spot_trading.spot.margin import cancel_margin_oco_order
    from Spot_trading.spot.margin import get_margin_oco_order
    from Spot_trading.spot.margin import get_margin_oco_orders
    from Spot_trading.spot.margin import get_margin_open_oco_orders
    from Spot_trading.spot.margin import cancel_isolated_margin_account
    from Spot_trading.spot.margin import enable_isolated_margin_account
    from Spot_trading.spot.margin import isolated_margin_account_limit
    from Spot_trading.spot.margin import margin_fee
    from Spot_trading.spot.margin import isolated_margin_fee
    from Spot_trading.spot.margin import isolated_margin_tier
    from Spot_trading.spot.margin import margin_order_usage
    from Spot_trading.spot.margin import margin_dust_log

    # SAVINGS
    from Spot_trading.spot.savings import savings_flexible_products
    from Spot_trading.spot.savings import savings_flexible_user_left_quota
    from Spot_trading.spot.savings import savings_purchase_flexible_product
    from Spot_trading.spot.savings import savings_flexible_user_redemption_quota
    from Spot_trading.spot.savings import savings_flexible_redeem
    from Spot_trading.spot.savings import savings_flexible_product_position
    from Spot_trading.spot.savings import savings_project_list
    from Spot_trading.spot.savings import savings_purchase_project
    from Spot_trading.spot.savings import savings_project_position
    from Spot_trading.spot.savings import savings_account
    from Spot_trading.spot.savings import savings_purchase_record
    from Spot_trading.spot.savings import savings_redemption_record
    from Spot_trading.spot.savings import savings_interest_history
    from Spot_trading.spot.savings import savings_change_position

    # Staking
    from Spot_trading.spot.staking import staking_product_list
    from Spot_trading.spot.staking import staking_purchase_product
    from Spot_trading.spot.staking import staking_redeem_product
    from Spot_trading.spot.staking import staking_product_position
    from Spot_trading.spot.staking import staking_history
    from Spot_trading.spot.staking import staking_set_auto_staking
    from Spot_trading.spot.staking import staking_product_quota

    # WALLET
    from Spot_trading.spot.wallet import system_status
    from Spot_trading.spot.wallet import coin_info
    from Spot_trading.spot.wallet import account_snapshot
    from Spot_trading.spot.wallet import disable_fast_withdraw
    from Spot_trading.spot.wallet import enable_fast_withdraw
    from Spot_trading.spot.wallet import withdraw
    from Spot_trading.spot.wallet import deposit_history
    from Spot_trading.spot.wallet import withdraw_history
    from Spot_trading.spot.wallet import deposit_address
    from Spot_trading.spot.wallet import account_status
    from Spot_trading.spot.wallet import api_trading_status
    from Spot_trading.spot.wallet import dust_log
    from Spot_trading.spot.wallet import user_universal_transfer
    from Spot_trading.spot.wallet import user_universal_transfer_history
    from Spot_trading.spot.wallet import transfer_dust
    from Spot_trading.spot.wallet import asset_dividend_record
    from Spot_trading.spot.wallet import asset_detail
    from Spot_trading.spot.wallet import trade_fee
    from Spot_trading.spot.wallet import funding_wallet
    from Spot_trading.spot.wallet import user_asset
    from Spot_trading.spot.wallet import api_key_permissions
    from Spot_trading.spot.wallet import bnb_convertible_assets

    # MINING
    from Spot_trading.spot.mining import mining_algo_list
    from Spot_trading.spot.mining import mining_coin_list
    from Spot_trading.spot.mining import mining_worker
    from Spot_trading.spot.mining import mining_worker_list
    from Spot_trading.spot.mining import mining_earnings_list
    from Spot_trading.spot.mining import mining_bonus_list
    from Spot_trading.spot.mining import mining_statistics_list
    from Spot_trading.spot.mining import mining_account_list
    from Spot_trading.spot.mining import mining_hashrate_resale_request
    from Spot_trading.spot.mining import mining_hashrate_resale_cancellation
    from Spot_trading.spot.mining import mining_hashrate_resale_list
    from Spot_trading.spot.mining import mining_hashrate_resale_details
    from Spot_trading.spot.mining import mining_account_earning

    # SUB-ACCOUNT
    from Spot_trading.spot.sub_account import sub_account_create
    from Spot_trading.spot.sub_account import sub_account_list
    from Spot_trading.spot.sub_account import sub_account_assets
    from Spot_trading.spot.sub_account import sub_account_deposit_address
    from Spot_trading.spot.sub_account import sub_account_deposit_history
    from Spot_trading.spot.sub_account import sub_account_status
    from Spot_trading.spot.sub_account import sub_account_enable_margin
    from Spot_trading.spot.sub_account import sub_account_margin_account
    from Spot_trading.spot.sub_account import sub_account_margin_account_summary
    from Spot_trading.spot.sub_account import sub_account_enable_futures
    from Spot_trading.spot.sub_account import sub_account_futures_transfer
    from Spot_trading.spot.sub_account import sub_account_margin_transfer
    from Spot_trading.spot.sub_account import sub_account_transfer_to_sub
    from Spot_trading.spot.sub_account import sub_account_transfer_to_master
    from Spot_trading.spot.sub_account import sub_account_transfer_sub_account_history
    from Spot_trading.spot.sub_account import sub_account_futures_asset_transfer_history
    from Spot_trading.spot.sub_account import sub_account_futures_asset_transfer
    from Spot_trading.spot.sub_account import sub_account_spot_summary
    from Spot_trading.spot.sub_account import sub_account_universal_transfer
    from Spot_trading.spot.sub_account import sub_account_universal_transfer_history
    from Spot_trading.spot.sub_account import sub_account_futures_account
    from Spot_trading.spot.sub_account import sub_account_futures_account_summary
    from Spot_trading.spot.sub_account import sub_account_futures_position_risk
    from Spot_trading.spot.sub_account import sub_account_spot_transfer_history
    from Spot_trading.spot.sub_account import sub_account_enable_leverage_token
    from Spot_trading.spot.sub_account import managed_sub_account_deposit
    from Spot_trading.spot.sub_account import managed_sub_account_assets
    from Spot_trading.spot.sub_account import managed_sub_account_withdraw
    from Spot_trading.spot.sub_account import sub_account_api_toggle_ip_restriction
    from Spot_trading.spot.sub_account import sub_account_api_add_ip
    from Spot_trading.spot.sub_account import sub_account_api_get_ip_restriction
    from Spot_trading.spot.sub_account import sub_account_api_delete_ip
    from Spot_trading.spot.sub_account import managed_sub_account_get_snapshot

    # FUTURES
    from Spot_trading.spot.futures import futures_transfer
    from Spot_trading.spot.futures import futures_transfer_history
    from Spot_trading.spot.futures import futures_loan_borrow
    from Spot_trading.spot.futures import futures_loan_borrow_history
    from Spot_trading.spot.futures import futures_loan_repay
    from Spot_trading.spot.futures import futures_loan_repay_history
    from Spot_trading.spot.futures import futures_loan_wallet
    from Spot_trading.spot.futures import futures_loan_configs
    from Spot_trading.spot.futures import futures_loan_calc_adjust_level
    from Spot_trading.spot.futures import futures_loan_calc_max_adjust_amount
    from Spot_trading.spot.futures import futures_loan_adjust_collateral
    from Spot_trading.spot.futures import futures_loan_adjust_collateral_history
    from Spot_trading.spot.futures import futures_loan_liquidation_history
    from Spot_trading.spot.futures import futures_loan_collateral_repay_limit
    from Spot_trading.spot.futures import futures_loan_collateral_repay_quote
    from Spot_trading.spot.futures import futures_loan_collateral_repay
    from Spot_trading.spot.futures import futures_loan_collateral_repay_result
    from Spot_trading.spot.futures import futures_loan_interest_history

    # BLVTs
    from Spot_trading.spot.blvt import blvt_info
    from Spot_trading.spot.blvt import subscribe_blvt
    from Spot_trading.spot.blvt import subscription_record
    from Spot_trading.spot.blvt import redeem_blvt
    from Spot_trading.spot.blvt import redemption_record
    from Spot_trading.spot.blvt import user_limit_info

    # BSwap
    from Spot_trading.spot.bswap import bswap_pools
    from Spot_trading.spot.bswap import bswap_liquidity
    from Spot_trading.spot.bswap import bswap_liquidity_add
    from Spot_trading.spot.bswap import bswap_liquidity_remove
    from Spot_trading.spot.bswap import bswap_liquidity_operation_record
    from Spot_trading.spot.bswap import bswap_request_quote
    from Spot_trading.spot.bswap import bswap_swap
    from Spot_trading.spot.bswap import bswap_swap_history
    from Spot_trading.spot.bswap import bswap_pool_configure
    from Spot_trading.spot.bswap import bswap_add_liquidity_preview
    from Spot_trading.spot.bswap import bswap_remove_liquidity_preview
    from Spot_trading.spot.bswap import bswap_unclaimed_rewards
    from Spot_trading.spot.bswap import bswap_claim_rewards
    from Spot_trading.spot.bswap import bswap_claimed_rewards

    # FIAT
    from Spot_trading.spot.fiat import fiat_order_history
    from Spot_trading.spot.fiat import fiat_payment_history

    # C2C
    from Spot_trading.spot.c2c import c2c_trade_history

    # CRYPTO LOANS
    from Spot_trading.spot.loan import loan_history
    from Spot_trading.spot.loan import loan_borrow
    from Spot_trading.spot.loan import loan_borrow_history
    from Spot_trading.spot.loan import loan_ongoing_orders
    from Spot_trading.spot.loan import loan_repay
    from Spot_trading.spot.loan import loan_repay_history
    from Spot_trading.spot.loan import loan_adjust_ltv
    from Spot_trading.spot.loan import loan_adjust_ltv_history

    # PAY
    from Spot_trading.spot.pay import pay_history

    # CONVERT
    from Spot_trading.spot.convert import convert_trade_history

    # REBATE
    from Spot_trading.spot.rebate import rebate_spot_history

    # NFT
    from Spot_trading.spot.nft import nft_transaction_history
    from Spot_trading.spot.nft import nft_deposit_history
    from Spot_trading.spot.nft import nft_withdraw_history
    from Spot_trading.spot.nft import nft_asset

    # Gift Card (Binance Code in the API documentation)
    from Spot_trading.spot.gift_card import gift_card_create_code
    from Spot_trading.spot.gift_card import gift_card_redeem_code
    from Spot_trading.spot.gift_card import gift_card_verify_code
    from Spot_trading.spot.gift_card import gift_card_rsa_public_key

    # Portfolio Margin
    from Spot_trading.spot.portfolio_margin import portfolio_margin_account
    from Spot_trading.spot.portfolio_margin import portfolio_margin_collateral_rate
    from Spot_trading.spot.portfolio_margin import portfolio_margin_bankruptcy_loan_amount
    from Spot_trading.spot.portfolio_margin import portfolio_margin_bankruptcy_loan_repay
