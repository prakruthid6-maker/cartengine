## 📘 Project Overview
E-commerce Shopping Agent with Role-Based Authentication

A production-ready, full-stack e-commerce platform with AI-powered shopping assistance, featuring secure authentication, role-based access control, real-time order tracking, advanced product filtering, voice search, dark mode, and comprehensive analytics. Built with FastAPI backend and vanilla JavaScript frontend.

## 🔐 Authentication System

### Login Credentials

**Customer Account:**
- Username: `user`
- Password: `user123`
- Access: Shopping, orders, cart, wishlist, chat

**Administrator Account:**
- Username: `admin`
- Password: `admin123`
- Access: All customer features + product management + analytics

### First Time Setup
1. Navigate to `login.html` in your browser
2. Enter credentials based on your role
3. Start shopping or managing products!

For detailed authentication documentation, see [AUTHENTICATION.md](./AUTHENTICATION.md)

Follow the steps below to set up and run the backend application.

## 🚀 Steps to Start the Backend App

1. **Navigate to the backend directory**  
   ```bash
   cd /workspace/e_commerce_shopping_agent/backend
   ```

2. **Install the required dependencies**  
   Before running the application, install all necessary Python packages using:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Google AI Studio Key**

   Visit https://aistudio.google.com/ using your personal gmail id and create an API Key. If you are a first time user you might have to create a new project in https://console.cloud.google.com/ first , import it here and then create API Key.

4. **Update env with Google AI Studio Key**

   Once the key is created copy the key value and update the below variable in .env file

   GOOGLE_API_KEY=<Use your key>

5. **Run the backend server**  
   Once the dependencies are installed, start the application with:  
   ```bash
   python main.py
   ```

## 🚀 Steps to Start the Frontend App

1. Find the `index.html` file inside the **frontend** directory.

2. **Configure the backend connection**  
   - Ensure that the **backend server** is up and running.  
   - Open the `apiService.js` file (usually located inside the `js` or `services` folder).  
   - Update the **host URL** or **API base URL** to match your backend’s running address.  
     Example:  
     ```js
     const API_CONFIG = {
      baseURL: "<BACKEND_URL>", // Configure the relevant backend url
      headers: {
      "Content-Type": "application/json",
      },
      };
     ```

3. **Start the frontend app**  
   - Open `login.html` in your browser (or right-click and choose **"Open with Live Server"**).
   - Login with demo credentials (see Authentication System above)
   - The application will redirect you to the main shopping page after successful login.

## 🎯 Features by Role

### 👤 Customer Features

#### 🛍️ Shopping Experience
- **Product Browsing**: View all products with beautiful card-based layout
- **Advanced Filters**: Filter by category, price range ($0-50, $50-100, $100-500, $500+), and badges
- **Search**: Text-based and voice-powered product search
- **Product Details**: View ratings, reviews, descriptions, and images
- **Product Comparison**: Compare up to 4 products side-by-side with detailed specs
- **Wishlist**: Save favorite products for later

#### 🛒 Cart & Orders
- **Shopping Cart**: Add/remove items, adjust quantities, view total
- **Checkout**: Complete purchase with delivery address and payment method
- **Order Tracking**: Real-time order status (Order Placed → Processing → Shipped → Out for Delivery → Delivered)
- **Order History**: View all past orders with details
- **Order Cancellation**: Cancel orders before delivery

#### 🤖 AI Assistant
- **Chat Interface**: Natural language queries for product search, recommendations, and order tracking
- **Smart Recommendations**: Budget-based, preference-based, and similar product suggestions
- **Order Management**: Track orders, cancel orders, check delivery estimates via chat
- **Product Reviews**: Add and view product reviews and ratings
- **Coupon Validation**: Check and apply discount coupons

#### 🎨 User Experience
- **Voice Search**: Speak commands like "Show electronics under 100"
- **Dark Mode**: Toggle between light and dark themes
- **Keyboard Shortcuts**: Quick access (Ctrl+C for cart, Ctrl+O for orders, etc.)
- **Live Activity Feed**: Real-time notifications of platform activity
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Fade-in, slide, zoom, and pulse effects

### 🛡️ Administrator Features

#### 📦 Product Management
- **Add Products**: Create new products with all details (name, category, price, description, image, badge)
- **Edit Products**: Update existing product information
- **Delete Products**: Remove products from catalog
- **Seller Management**: Add sellers with location and rating information

#### 📊 Analytics & Insights
- **Dashboard**: View total products, average price, average rating, cart items, orders, categories
- **Category Breakdown**: Visual bar charts showing products per category
- **Product Statistics**: Count by category, highest-rated category, most-reviewed products
- **Audit Tools**: Recently added products, products added in last 7 days, monthly additions
- **Seller Analytics**: Products by seller, top-rated sellers, location-based insights

#### 💰 Promotions
- **Coupon Creation**: Generate discount codes with expiry dates
- **Coupon Management**: Validate and track coupon usage

#### 🔧 All Customer Features
- Admins have full access to all customer features plus management capabilities

## 📁 Project Structure

```
Los_codigos_782/
├── backend/
│   ├── main.py                      # FastAPI server with CORS
│   ├── techai_agent/                # AI agent configuration
│   │   ├── agent.py                 # Agent setup
│   │   ├── tools.py                 # 50+ tool functions
│   │   ├── prompt.py                # Agent prompts
│   │   └── .env                     # Google AI API key
│   ├── routers/
│   │   ├── products.py              # Product CRUD endpoints
│   │   └── orders.py                # Order & cancellation endpoints
│   ├── services/
│   │   └── product_service.py       # Business logic layer
│   ├── repos/
│   │   └── products_repo.py         # Database operations
│   ├── models/
│   │   └── data_models.py           # Pydantic models
│   ├── products.db                  # SQLite database (10 tables)
│   ├── requirements.txt             # Python dependencies
│   ├── populate_products.py         # Sample data seeder
│   └── migrate_*.py                 # Database migrations
├── frontend/
│   ├── login.html                   # Login page (START HERE)
│   ├── index.html                   # Main shopping page
│   ├── pages/
│   │   └── chat.html                # AI customer service chat
│   ├── scripts/
│   │   ├── auth.js                  # Authentication & session management
│   │   ├── login.js                 # Login form handling
│   │   ├── main.js                  # Main app (3000+ lines)
│   │   └── chat.js                  # Chat interface with streaming
│   ├── services/
│   │   └── apiService.js            # API client with SSE support
│   └── styles/
│       ├── login.css                # Login page styles
│       ├── main.css                 # Main app styles with animations
│       └── chat.css                 # Chat interface styles
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
└── FEATURES.md                      # Complete feature list (50+ tools)
```

## 🔒 Security Notes

- Current implementation uses demo credentials for testing
- For production deployment, implement:
  - JWT token authentication
  - Password hashing (bcrypt)
  - HTTPS only
  - Rate limiting
  - Session timeout
  - See AUTHENTICATION.md for full production checklist

## 🔄 Complete User Workflow

### First-Time User Journey

1. **Login** (`login.html`)
   - Enter credentials (user/user123 or admin/admin123)
   - System validates and creates session in localStorage
   - Redirects to main shopping page

2. **Browse Products** (`index.html`)
   - View all products in card layout with animations
   - See product images, prices, ratings, reviews, badges
   - User info and role displayed in header

3. **Filter & Search**
   - Use category dropdown (Electronics, Clothing, Books, etc.)
   - Select price range (Under $50, $50-$100, etc.)
   - Filter by badges (New, Sale, etc.)
   - Try voice search: Click microphone, say "Show electronics under 100"

4. **Product Actions**
   - **Add to Cart**: Click cart icon on product card
   - **Compare**: Click compare icon (up to 4 products)
   - **View Details**: See full description and reviews

5. **Shopping Cart**
   - Click cart icon in header (shows item count)
   - Adjust quantities with +/- buttons
   - Remove items with trash icon
   - View total price
   - Click "Checkout" to proceed

6. **Checkout Process**
   - Enter delivery address
   - Select payment method (Credit Card, Debit Card, PayPal, Cash on Delivery)
   - Click "Place Order"
   - Backend creates order with unique ID (ORD-XXXXXXXX)
   - Order saved to localStorage and backend database
   - Cart cleared automatically

7. **Order Management**
   - Click "Orders" in header to view all orders
   - See order ID, status, date, items, total, address
   - Track order status progression
   - Cancel orders (if not Delivered/Cancelled)

8. **AI Chat Assistant** (`pages/chat.html`)
   - Click "Chat" in header
   - Create new session or continue existing
   - Ask natural language questions:
     - "Show me products under $50"
     - "Track my order ORD-12345678"
     - "Recommend products for $100 budget in Electronics"
     - "Add product elec-001 to my wishlist"
     - "Show reviews for product elec-001"
     - "Validate coupon code SAVE20"
     - "Cancel my order ORD-12345678"
   - Get instant AI-powered responses
   - Upload images for visual search

9. **Additional Features**
   - **Compare Products**: Click compare icon in header, view side-by-side table
   - **Dark Mode**: Click moon/sun icon to toggle theme
   - **Keyboard Shortcuts**: Press `?` to see all shortcuts
   - **Analytics** (Admin only): View dashboard with statistics

### Admin Workflow

1. **Login as Admin** (admin/admin123)
2. **Product Management**
   - Click "Add Product" button
   - Fill form: ID, name, category, description, price, rating, reviews, image URL, badge
   - Click "Save" to create product
   - Edit: Click pencil icon on product card
   - Delete: Click trash icon (with confirmation)

3. **Analytics Dashboard**
   - Click "Analytics" in header
   - View total products, average price, average rating
   - See cart items, total orders, categories count
   - Visual category breakdown with bar charts

4. **Seller Management** (via Chat)
   - Use chat to add sellers: "Add seller with ID sell-001, name TechStore, location New York, rating 4.5"
   - Query seller stats: "Get products count by seller TechStore"

5. **Coupon Management** (via Chat)
   - Create coupons: "Create coupon SAVE20 with 20% discount expiring 2024-12-31"
   - Validate: "Validate coupon code SAVE20"

## 🛠️ Technical Architecture

### Backend (FastAPI + SQLite)
- **Framework**: FastAPI with Uvicorn server
- **AI Agent**: Google ADK (Agent Development Kit) with Gemini
- **Database**: SQLite with 10 tables (products, sellers, orders, payments, order_tracking, wishlist, reviews, coupons)
- **API**: RESTful endpoints + SSE streaming for chat
- **Tools**: 50+ Python functions for all operations
- **CORS**: Configured for frontend access

### Frontend (Vanilla JavaScript)
- **No Framework**: Pure HTML, CSS, JavaScript
- **Authentication**: localStorage-based session management
- **API Client**: Fetch API with SSE support for streaming
- **State Management**: localStorage for cart, orders, compare list, theme
- **Animations**: CSS transitions and keyframes
- **Icons**: Font Awesome 6
- **Markdown**: Marked.js for chat rendering

### Database Schema (10 Tables)
1. **products**: id, name, categoryId, description, price, ratings, reviews, image, badge, seller_id, created_at
2. **sellers**: seller_id, name, location, rating
3. **orders**: order_id, product_id, user_id, quantity, total_price, status, delivery_address, order_date
4. **payments**: payment_id, order_id, amount, method, status, timestamp
5. **order_tracking**: tracking_id, order_id, status, location, timestamp
6. **wishlist**: wishlist_id, user_id, product_id, added_date
7. **reviews**: review_id, product_id, user_id, rating, comment, review_date
8. **coupons**: coupon_code, discount_percent, expiry_date, status

### AI Agent Tools (50+ Functions)
- **Shopping**: fetch_products, search_products_by_category, filter_products_by_price, get_product_details, compare_products_tool
- **Orders**: create_order, get_order_details, get_user_orders, cancel_order_tool
- **Tracking**: track_order, update_order_status, get_estimated_delivery, get_delivery_history
- **Payments**: process_payment, get_payment_status
- **Recommendations**: recommend_products_by_budget, recommend_similar_products, recommend_by_preferences, get_best_deals
- **Wishlist**: add_to_wishlist_tool, get_wishlist_tool, remove_from_wishlist_tool
- **Reviews**: add_review_tool, get_product_reviews_tool
- **Coupons**: create_coupon_tool, validate_coupon_tool
- **Analytics**: get_analytics_summary, get_total_products_count, get_category_with_highest_rating
- **Admin**: add_new_product, update_product, delete_product, add_seller
- **Advanced**: search_products_advanced, get_trending_products, filter_products_by_category_and_price

## 🎨 UI/UX Features

### Animations
- **Product Cards**: Fade-in on load, scale on hover, shadow transitions
- **Buttons**: Ripple effect, gradient backgrounds, smooth hover
- **Modals**: Slide-down, zoom-in animations
- **Badges**: Pulse animation for "New" and "Sale"
- **Images**: Zoom on hover
- **Loading**: Spinner animation
- **Toasts**: Slide-in notifications

### Responsive Design
- Mobile-first approach
- Flexible grid layout
- Touch-friendly buttons
- Adaptive font sizes

### Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- High contrast mode support

## 🐛 Troubleshooting

**Issue: Can't access pages after login**
- Clear browser localStorage: `localStorage.clear()`
- Try logging in again
- Check browser console for errors

**Issue: Admin features not showing**
- Verify you logged in with admin credentials (admin/admin123)
- Check console: `console.log(localStorage.getItem('userSession'))`
- Ensure role is set to 'admin'

**Issue: Backend connection failed**
- Ensure backend is running: `python main.py`
- Check port 8080 is not in use
- Verify `apiService.js` has correct URL
- Check CORS settings in `main.py`

**Issue: Voice search not working**
- Use Chrome/Edge (best support for Web Speech API)
- Allow microphone permissions
- Speak clearly and wait for "Listening..." indicator

**Issue: Chat not responding**
- Check Google API key in `.env` file
- Verify backend logs for errors
- Create new session if stuck
- Check network tab for SSE connection

**Issue: Orders not saving**
- Check backend is running
- Verify database file exists (`products.db`)
- Check browser console for API errors
- Ensure user_id is set correctly

**Issue: Products not loading**
- Run `python populate_products.py` to seed database
- Check database has products: `sqlite3 products.db "SELECT COUNT(*) FROM products;"`
- Verify API endpoint: `http://localhost:8080/products/all`

## 📚 Additional Documentation

- [FEATURES.md](./FEATURES.md) - Complete feature list with 50+ tools and detailed descriptions

## 🚀 Deployment Notes

### Production Checklist
- [ ] Replace demo credentials with real authentication (JWT)
- [ ] Hash passwords with bcrypt
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS only
- [ ] Add rate limiting
- [ ] Implement session timeout
- [ ] Use production database (PostgreSQL/MySQL)
- [ ] Add logging and monitoring
- [ ] Optimize images and assets
- [ ] Enable CDN for static files
- [ ] Add error tracking (Sentry)
- [ ] Implement backup strategy

### Environment Variables
```bash
GOOGLE_API_KEY=your_api_key_here
PORT=8080
DATABASE_URL=sqlite:///products.db
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 🤝 Contributing

This is a complete e-commerce platform with 50+ features. To extend:
1. Add new tools in `backend/techai_agent/tools.py`
2. Create new API endpoints in `backend/routers/`
3. Update frontend in `frontend/scripts/main.js`
4. Add database migrations in `backend/migrate_*.py`
5. Update documentation

## 📄 License

This project is for educational purposes.