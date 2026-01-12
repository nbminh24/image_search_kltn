# Tài liệu Database Schema

## 1. Bảng `admins`
Quản lý thông tin tài khoản quản trị viên

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho quản trị viên | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên của quản trị viên | character varying | Nullable |
| 3 | email | Địa chỉ email của quản trị viên | character varying | NOT NULL, UNIQUE |
| 4 | password_hash | Mật khẩu đã được mã hóa | text | NOT NULL |
| 5 | role | Vai trò của quản trị viên | character varying | DEFAULT 'admin' |
| 6 | created_at | Thời gian tạo tài khoản | timestamp with time zone | DEFAULT now() |

## 2. Bảng `cart_items`
Quản lý các sản phẩm trong giỏ hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho mục giỏ hàng | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | cart_id | Khóa ngoại tham chiếu đến bảng carts | bigint | NOT NULL, FOREIGN KEY → carts(id) |
| 3 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
| 4 | quantity | Số lượng sản phẩm trong giỏ | integer | NOT NULL, CHECK (quantity > 0) |

## 3. Bảng `carts`
Quản lý giỏ hàng của khách hàng hoặc phiên truy cập

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho giỏ hàng | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | UNIQUE, FOREIGN KEY → customers(id) |
| 3 | session_id | ID phiên cho khách vãng lai | character varying | UNIQUE |
| 4 | created_at | Thời gian tạo giỏ hàng | timestamp with time zone | DEFAULT now() |
| 5 | updated_at | Thời gian cập nhật giỏ hàng | timestamp with time zone | DEFAULT now() |

## 4. Bảng `categories`
Quản lý danh mục sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho danh mục | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên danh mục | character varying | NOT NULL |
| 3 | slug | Đường dẫn thân thiện URL | character varying | NOT NULL, UNIQUE |
| 4 | status | Trạng thái danh mục | character varying | DEFAULT 'active' |
| 5 | deleted_at | Thời gian xóa danh mục (xóa mềm) | timestamp with time zone | Nullable |

## 5. Bảng `chat_messages`
Quản lý tin nhắn trong hệ thống chat

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho tin nhắn | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | session_id | Khóa ngoại tham chiếu đến phiên chat | bigint | FOREIGN KEY → chat_sessions(id) |
| 3 | sender | Người gửi tin nhắn | character varying | NOT NULL |
| 4 | message | Nội dung tin nhắn | text | NOT NULL |
| 5 | is_read | Trạng thái đã đọc | boolean | DEFAULT false |
| 6 | created_at | Thời gian gửi tin nhắn | timestamp with time zone | DEFAULT now() |
| 7 | image_url | URL hình ảnh đính kèm | text | Nullable |
| 8 | custom | Dữ liệu tùy chỉnh dạng JSON | jsonb | Nullable |
| 9 | buttons | Các nút tương tác dạng JSON | jsonb | Nullable |

## 6. Bảng `chat_sessions`
Quản lý phiên chat giữa khách hàng và hệ thống

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho phiên chat | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | FOREIGN KEY → customers(id) |
| 3 | visitor_id | ID cho khách vãng lai | character varying | Nullable |
| 4 | created_at | Thời gian tạo phiên chat | timestamp with time zone | DEFAULT now() |
| 5 | updated_at | Thời gian cập nhật phiên chat | timestamp with time zone | DEFAULT now() |
| 6 | status | Trạng thái phiên chat | character varying | DEFAULT 'active', CHECK (status IN ('bot', 'human_pending', 'human_active', 'closed')) |
| 7 | assigned_admin_id | Quản trị viên được gán xử lý | bigint | FOREIGN KEY → admins(id) |
| 8 | handoff_requested_at | Thời gian yêu cầu chuyển sang nhân viên | timestamp with time zone | Nullable |
| 9 | handoff_accepted_at | Thời gian chấp nhận xử lý | timestamp with time zone | Nullable |
| 10 | handoff_reason | Lý do chuyển sang nhân viên | character varying | Nullable |

## 7. Bảng `colors`
Quản lý màu sắc sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho màu sắc | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên màu sắc | character varying | NOT NULL |
| 3 | hex_code | Mã màu dạng hex | character varying | Nullable |

## 8. Bảng `customer_addresses`
Quản lý địa chỉ giao hàng của khách hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho địa chỉ | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | NOT NULL, FOREIGN KEY → customers(id) |
| 3 | is_default | Đánh dấu địa chỉ mặc định | boolean | DEFAULT false |
| 4 | address_type | Loại địa chỉ | character varying | DEFAULT 'Home' |
| 5 | street_address | Địa chỉ đường phố chi tiết | text | NOT NULL |
| 6 | phone_number | Số điện thoại liên hệ | character varying | NOT NULL |
| 7 | province | Tỉnh/Thành phố | character varying | Nullable |
| 8 | district | Quận/Huyện | character varying | Nullable |
| 9 | ward | Phường/Xã | character varying | Nullable |
| 10 | latitude | Vĩ độ địa lý | numeric | Nullable |
| 11 | longitude | Kinh độ địa lý | numeric | Nullable |
| 12 | address_source | Nguồn gốc địa chỉ | character varying | DEFAULT 'manual' |

## 9. Bảng `customers`
Quản lý thông tin tài khoản khách hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho khách hàng | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên của khách hàng | character varying | Nullable |
| 3 | email | Địa chỉ email của khách hàng | character varying | NOT NULL, UNIQUE |
| 4 | password_hash | Mật khẩu đã được mã hóa | text | Nullable |
| 5 | status | Trạng thái tài khoản | character varying | DEFAULT 'active' |
| 6 | refresh_token | Token làm mới phiên đăng nhập | text | Nullable |
| 7 | refresh_token_expires | Thời gian hết hạn refresh token | timestamp with time zone | Nullable |
| 8 | created_at | Thời gian đăng ký tài khoản | timestamp with time zone | DEFAULT now() |
| 9 | updated_at | Thời gian cập nhật thông tin | timestamp with time zone | DEFAULT now() |
| 10 | deleted_at | Thời gian xóa tài khoản (xóa mềm) | timestamp with time zone | Nullable |

## 10. Bảng `order_items`
Quản lý các sản phẩm trong đơn hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho mục đơn hàng | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | order_id | Khóa ngoại tham chiếu đến đơn hàng | bigint | NOT NULL, FOREIGN KEY → orders(id) |
| 3 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
| 4 | quantity | Số lượng sản phẩm | integer | NOT NULL |
| 5 | price_at_purchase | Giá tại thời điểm mua | numeric | NOT NULL |

## 11. Bảng `order_status_history`
Lưu trữ lịch sử thay đổi trạng thái đơn hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | order_id | Khóa ngoại tham chiếu đến đơn hàng | bigint | NOT NULL, FOREIGN KEY → orders(id) |
| 3 | status | Trạng thái mới của đơn hàng | character varying | NOT NULL |
| 4 | admin_id | Quản trị viên thực hiện thay đổi | bigint | Nullable |
| 5 | created_at | Thời gian thay đổi trạng thái | timestamp with time zone | DEFAULT now() |
| 6 | note | Ghi chú về thay đổi | text | Nullable |

## 12. Bảng `orders`
Quản lý đơn hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho đơn hàng | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | FOREIGN KEY → customers(id) |
| 3 | customer_email | Email khách hàng | character varying | Nullable |
| 4 | shipping_address | Địa chỉ giao hàng | text | NOT NULL |
| 5 | shipping_phone | Số điện thoại nhận hàng | character varying | NOT NULL |
| 6 | shipping_city | Tỉnh/Thành phố giao hàng | character varying | Nullable |
| 7 | shipping_district | Quận/Huyện giao hàng | character varying | Nullable |
| 8 | shipping_ward | Phường/Xã giao hàng | character varying | Nullable |
| 9 | fulfillment_status | Trạng thái xử lý đơn hàng | character varying | DEFAULT 'pending' |
| 10 | payment_status | Trạng thái thanh toán | character varying | DEFAULT 'unpaid' |
| 11 | payment_method | Phương thức thanh toán | character varying | DEFAULT 'cod' |
| 12 | shipping_fee | Phí vận chuyển | numeric | DEFAULT 0 |
| 13 | total_amount | Tổng giá trị đơn hàng | numeric | NOT NULL |
| 14 | created_at | Thời gian tạo đơn hàng | timestamp with time zone | DEFAULT now() |
| 15 | updated_at | Thời gian cập nhật đơn hàng | timestamp with time zone | DEFAULT now() |
| 16 | order_number | Mã đơn hàng | character varying | Nullable |
| 17 | shipping_method | Phương thức vận chuyển | character varying | DEFAULT 'standard' |
| 18 | tracking_number | Mã vận đơn | character varying | Nullable |
| 19 | carrier_name | Tên đơn vị vận chuyển | character varying | Nullable |
| 20 | estimated_delivery_from | Ngày giao hàng dự kiến (từ) | date | Nullable |
| 21 | estimated_delivery_to | Ngày giao hàng dự kiến (đến) | date | Nullable |
| 22 | actual_delivery_date | Ngày giao hàng thực tế | date | Nullable |
| 23 | cancelled_at | Thời gian hủy đơn | timestamp with time zone | Nullable |
| 24 | cancel_reason | Lý do hủy đơn | character varying | Nullable |
| 25 | cancelled_by_customer_id | Khách hàng thực hiện hủy | bigint | Nullable |
| 26 | refund_status | Trạng thái hoàn tiền | character varying | DEFAULT 'pending' |
| 27 | refund_amount | Số tiền hoàn lại | numeric | Nullable |

## 13. Bảng `pages`
Quản lý các trang nội dung tĩnh

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho trang | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | title | Tiêu đề trang | character varying | NOT NULL |
| 3 | slug | Đường dẫn thân thiện URL | character varying | NOT NULL, UNIQUE |
| 4 | content | Nội dung trang | text | Nullable |
| 5 | status | Trạng thái trang | character varying | DEFAULT 'Draft' |
| 6 | created_at | Thời gian tạo trang | timestamp with time zone | DEFAULT now() |
| 7 | updated_at | Thời gian cập nhật trang | timestamp with time zone | DEFAULT now() |

## 14. Bảng `payments`
Quản lý thông tin thanh toán

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho giao dịch | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | order_id | Khóa ngoại tham chiếu đến đơn hàng | bigint | FOREIGN KEY → orders(id) |
| 3 | transaction_id | Mã giao dịch từ nhà cung cấp | character varying | Nullable |
| 4 | amount | Số tiền thanh toán | numeric | NOT NULL |
| 5 | provider | Nhà cung cấp dịch vụ thanh toán | character varying | Nullable |
| 6 | payment_method | Phương thức thanh toán | character varying | Nullable |
| 7 | status | Trạng thái giao dịch | character varying | Nullable |
| 8 | response_data | Dữ liệu phản hồi từ nhà cung cấp | jsonb | Nullable |
| 9 | created_at | Thời gian tạo giao dịch | timestamp with time zone | DEFAULT now() |

## 15. Bảng `product_images`
Quản lý hình ảnh sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho hình ảnh | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
| 3 | image_url | URL hình ảnh | text | NOT NULL |
| 4 | is_main | Đánh dấu hình ảnh chính | boolean | DEFAULT false |

## 16. Bảng `product_notifications`
Quản lý thông báo sản phẩm cho khách hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | character varying | PRIMARY KEY |
| 2 | user_id | Khóa ngoại tham chiếu đến khách hàng | bigint | NOT NULL, FOREIGN KEY → customers(id) |
| 3 | product_id | Khóa ngoại tham chiếu đến sản phẩm | bigint | NOT NULL, FOREIGN KEY → products(id) |
| 4 | size | Kích thước quan tâm | character varying | Nullable |
| 5 | price_condition | Điều kiện giá để thông báo | numeric | Nullable |
| 6 | status | Trạng thái thông báo | character varying | DEFAULT 'active' |
| 7 | created_at | Thời gian đăng ký thông báo | timestamp with time zone | DEFAULT now() |
| 8 | notified_at | Thời gian đã gửi thông báo | timestamp with time zone | Nullable |

## 17. Bảng `product_reviews`
Quản lý đánh giá sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho đánh giá | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
| 3 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | NOT NULL, FOREIGN KEY → customers(id) |
| 4 | order_id | Khóa ngoại tham chiếu đến đơn hàng | bigint | NOT NULL, FOREIGN KEY → orders(id) |
| 5 | rating | Điểm đánh giá | integer | NOT NULL, CHECK (rating >= 1 AND rating <= 5) |
| 6 | comment | Nhận xét của khách hàng | text | Nullable |
| 7 | status | Trạng thái duyệt đánh giá | character varying | DEFAULT 'pending' |
| 8 | created_at | Thời gian tạo đánh giá | timestamp with time zone | DEFAULT now() |

## 18. Bảng `product_variants`
Quản lý các biến thể sản phẩm (size, màu sắc)

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho biến thể | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | product_id | Khóa ngoại tham chiếu đến sản phẩm | bigint | NOT NULL, FOREIGN KEY → products(id) |
| 3 | size_id | Khóa ngoại tham chiếu đến kích thước | bigint | FOREIGN KEY → sizes(id) |
| 4 | color_id | Khóa ngoại tham chiếu đến màu sắc | bigint | FOREIGN KEY → colors(id) |
| 5 | name | Tên biến thể | character varying | Nullable |
| 6 | sku | Mã SKU duy nhất | character varying | NOT NULL, UNIQUE |
| 7 | total_stock | Tổng số lượng tồn kho | integer | DEFAULT 0 |
| 8 | reserved_stock | Số lượng đã đặt trước | integer | DEFAULT 0 |
| 9 | reorder_point | Ngưỡng nhập hàng lại | integer | DEFAULT 0 |
| 10 | status | Trạng thái biến thể | character varying | DEFAULT 'active' |
| 11 | version | Phiên bản (optimistic locking) | integer | DEFAULT 1 |
| 12 | deleted_at | Thời gian xóa (xóa mềm) | timestamp with time zone | Nullable |

## 19. Bảng `products`
Quản lý thông tin sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho sản phẩm | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | category_id | Khóa ngoại tham chiếu đến danh mục | bigint | FOREIGN KEY → categories(id) |
| 3 | name | Tên sản phẩm | character varying | NOT NULL |
| 4 | slug | Đường dẫn thân thiện URL | character varying | NOT NULL, UNIQUE |
| 5 | description | Mô tả ngắn sản phẩm | text | Nullable |
| 6 | full_description | Mô tả chi tiết sản phẩm | text | Nullable |
| 7 | cost_price | Giá vốn | numeric | Nullable |
| 8 | selling_price | Giá bán | numeric | NOT NULL |
| 9 | status | Trạng thái sản phẩm | character varying | DEFAULT 'active' |
| 10 | thumbnail_url | URL hình đại diện | text | Nullable |
| 11 | average_rating | Điểm đánh giá trung bình | numeric | DEFAULT 0.00 |
| 12 | total_reviews | Tổng số đánh giá | integer | DEFAULT 0 |
| 13 | attributes | Thuộc tính mở rộng dạng JSON | jsonb | DEFAULT '{}' |
| 14 | created_at | Thời gian tạo sản phẩm | timestamp with time zone | DEFAULT now() |
| 15 | updated_at | Thời gian cập nhật sản phẩm | timestamp with time zone | DEFAULT now() |
| 16 | deleted_at | Thời gian xóa sản phẩm (xóa mềm) | timestamp with time zone | Nullable |

## 20. Bảng `promotion_products`
Quản lý sản phẩm tham gia chương trình khuyến mãi

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | promotion_id | Khóa ngoại tham chiếu đến chương trình khuyến mãi | bigint | NOT NULL, FOREIGN KEY → promotions(id) |
| 3 | product_id | Khóa ngoại tham chiếu đến sản phẩm | bigint | NOT NULL, FOREIGN KEY → products(id) |
| 4 | flash_sale_price | Giá flash sale | numeric | NOT NULL |

## 21. Bảng `promotion_usage`
Theo dõi việc sử dụng mã khuyến mãi

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | promotion_id | Khóa ngoại tham chiếu đến chương trình khuyến mãi | bigint | NOT NULL, FOREIGN KEY → promotions(id) |
| 3 | order_id | Khóa ngoại tham chiếu đến đơn hàng | bigint | NOT NULL, FOREIGN KEY → orders(id) |
| 4 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | NOT NULL, FOREIGN KEY → customers(id) |
| 5 | created_at | Thời gian sử dụng khuyến mãi | timestamp with time zone | DEFAULT now() |

## 22. Bảng `promotions`
Quản lý chương trình khuyến mãi

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho chương trình | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên chương trình khuyến mãi | character varying | NOT NULL |
| 3 | type | Loại khuyến mãi | character varying | NOT NULL |
| 4 | discount_value | Giá trị giảm giá | numeric | NOT NULL |
| 5 | discount_type | Loại giảm giá (%, số tiền cố định) | character varying | NOT NULL |
| 6 | number_limited | Số lượng mã giới hạn | integer | Nullable |
| 7 | start_date | Ngày bắt đầu | timestamp with time zone | NOT NULL |
| 8 | end_date | Ngày kết thúc | timestamp with time zone | NOT NULL |
| 9 | status | Trạng thái chương trình | character varying | DEFAULT 'scheduled' |

## 23. Bảng `restock_batches`
Quản lý các đợt nhập hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho đợt nhập | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | admin_id | Quản trị viên thực hiện nhập hàng | bigint | NOT NULL |
| 3 | type | Loại nhập hàng | character varying | DEFAULT 'Manual' |
| 4 | created_at | Thời gian tạo đợt nhập | timestamp with time zone | DEFAULT now() |

## 24. Bảng `restock_items`
Quản lý chi tiết sản phẩm trong đợt nhập hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | batch_id | Khóa ngoại tham chiếu đến đợt nhập hàng | bigint | NOT NULL, FOREIGN KEY → restock_batches(id) |
| 3 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
| 4 | quantity | Số lượng nhập | integer | NOT NULL, CHECK (quantity > 0) |

## 25. Bảng `sizes`
Quản lý kích thước sản phẩm

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho kích thước | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | name | Tên kích thước | character varying | NOT NULL |
| 3 | sort_order | Thứ tự sắp xếp | integer | DEFAULT 0 |

## 26. Bảng `support_ticket_replies`
Quản lý câu trả lời cho ticket hỗ trợ

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho câu trả lời | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | ticket_id | Khóa ngoại tham chiếu đến ticket | bigint | NOT NULL, FOREIGN KEY → support_tickets(id) |
| 3 | admin_id | Quản trị viên trả lời | bigint | Nullable |
| 4 | body | Nội dung trả lời | text | NOT NULL |
| 5 | created_at | Thời gian trả lời | timestamp with time zone | DEFAULT now() |

## 27. Bảng `support_tickets`
Quản lý ticket hỗ trợ khách hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất cho ticket | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | ticket_code | Mã ticket duy nhất | character varying | NOT NULL, UNIQUE |
| 3 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | FOREIGN KEY → customers(id) |
| 4 | customer_email | Email khách hàng | character varying | Nullable |
| 5 | subject | Tiêu đề ticket | character varying | NOT NULL |
| 6 | status | Trạng thái xử lý | character varying | DEFAULT 'pending' |
| 7 | source | Nguồn gốc ticket | character varying | DEFAULT 'contact_form' |
| 8 | message | Nội dung yêu cầu | text | Nullable |
| 9 | priority | Độ ưu tiên | character varying | DEFAULT 'medium' |
| 10 | created_at | Thời gian tạo ticket | timestamp with time zone | DEFAULT now() |
| 11 | updated_at | Thời gian cập nhật ticket | timestamp with time zone | DEFAULT now() |

## 28. Bảng `wishlist_items`
Quản lý danh sách yêu thích của khách hàng

| STT | Tên thuộc tính | Diễn giải | Kiểu dữ liệu | Ràng buộc |
|-----|---------------|-----------|--------------|-----------|
| 1 | id | Khóa chính, định danh duy nhất | bigint | PRIMARY KEY, GENERATED ALWAYS AS IDENTITY |
| 2 | customer_id | Khóa ngoại tham chiếu đến khách hàng | bigint | NOT NULL, FOREIGN KEY → customers(id) |
| 3 | variant_id | Khóa ngoại tham chiếu đến biến thể sản phẩm | bigint | NOT NULL, FOREIGN KEY → product_variants(id) |
