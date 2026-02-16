from google.adk.agents import LlmAgent
from techai_agent.prompt import *
from techai_agent.tools import *

Model = "gemini-2.5-flash"
root_agent = LlmAgent(
    name="tech_agent",
    model=Model,
    description="Agent that helps users shop a curated selection of Electronics, Fashion, Home essentials, and Sports gear, complete with customer ratings and deals. ", 
    instruction=ROOT_AGENT_PROMPT,
    tools= [
        # Product browsing & search
        fetch_products,
        search_products_by_category,
        filter_products_by_price,
        get_product_details,
        get_top_rated_products,
        get_products_on_sale,
        search_products_advanced,
        get_trending_products,
        filter_products_by_category_and_price,
        get_all_categories,
        get_all_badges,
        
        # Cart operations (PERSISTENT - NEW!)
        add_to_cart,
        get_cart_summary,
        update_cart_item,
        remove_from_cart_tool,
        clear_cart_tool,
        
        # Inventory & stock (REAL DATA - NEW!)
        check_product_availability,
        update_inventory_tool,
        set_product_discount,
        
        # Product comparison & shipping
        compare_products,
        compare_products_tool,
        get_shipping_info,
        
        # Coupons
        apply_coupon,
        create_coupon_tool,
        validate_coupon_tool,
        
        # Product management
        add_new_product,
        delete_product,
        update_product,
        
        # Analytics
        get_total_products_count,
        get_products_count_by_category,
        get_category_with_highest_rating,
        get_product_with_most_reviews,
        get_most_recently_added_product,
        get_products_added_last_7_days,
        get_category_with_most_additions_this_month,
        get_analytics_summary,
        
        # Sellers
        add_seller,
        get_products_count_by_seller,
        get_seller_with_most_5star_products,
        get_location_with_highest_product_count,
        
        # Orders & payments
        create_order,
        get_order_details,
        get_user_orders,
        process_payment,
        get_payment_status,
        track_order,
        update_order_status,
        get_estimated_delivery,
        get_delivery_history,
        cancel_order_tool,
        
        # Recommendations
        recommend_products_by_budget,
        recommend_similar_products,
        recommend_by_preferences,
        get_best_deals,
        
        # Wishlist
        add_to_wishlist_tool,
        get_wishlist_tool,
        remove_from_wishlist_tool,
        
        # Reviews
        add_review_tool,
        get_product_reviews_tool,
    ]
)