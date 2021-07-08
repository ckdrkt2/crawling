{% load api_tags %}
<!-- <span>{{widget_option.product_name}}</span>
<span>{{widget_option.product_price}}</span> -->


<div class="widget_w">
    <div style="display: flex;flex-wrap: wrap;margin: 0 -2%;">
    {% for product in data_list %}
    <div class="widget_item_container">
        <div class="widget_item">
            <div class="widget_item_product_img" style="background-image:url('{{product.list_image}}')" onclick='redirect_to_product("{{product.product_no}}")'></div>
            {% if widget_option.product_name or widget_option.product_price %}
            <div class="widget_item_product_info" onclick='redirect_to_product("{{product.product_no}}")'>
                {% if widget_option.product_name %}
                <div class="widget_item_product_info_name">{{product.product_name}}</div>
                {% endif %}
                {% if widget_option.product_price %}
                <div class="widget_item_product_info_price">{{product.price}}원</div>
                {% endif %}
            </div>
            {% endif %}

            {% if widget_option.ratings or widget_option.review_num %}
            <div class="widget_item_summary">
                
                {% if widget_option.ratings %}
                
                
                
                <div class="widget_total_ratings_star">
                    <div class="widget_total_ratings_star_empty">
                        <div  class="widget_total_ratings_star_container">
                            {% include 'module/alph_star_empty.html' %}
                        </div>
                    </div>

                    <div class="widget_total_ratings_star_full" style="width: {{product.review_ratings|floatformat:1|rating_width}}%">
                        <div  class="widget_total_ratings_star_container">
                            {% include 'module/alph_star_full.html' %}
                        </div>
                    </div>
                </div>
                <div style="flex-grow:1"></div>

                <div class='widget_item_summary_ratings_1'>평점</div>
                <div class='widget_item_summary_ratings_2'>{{product.review_ratings|floatformat:1}}</div>
                {% endif %}

                {% if widget_option.review_num %}
                <div class='widget_item_summary_num_1'>상품평수 </div>
                <div class='widget_item_summary_num_2'>{{product.review_number|floatformat:"0"}}개</div>
                {% endif %}
            </div>
            {% endif %}
            <div class="widget_item_review_container">
            {% for review in product.review_list  %}
                <div class="widget_item_review" onclick='review_detail_{{widget_id}}({{review.id}},{{product.product_no}})'>
                    {% if review.review_video.all and review.review_video.all.0.thumbnail %}
                    <div class="widget_item_review_image">
                        <video autoplay loop muted playsinline  class="lozad">
                            <source data-src="{{review.review_video.all.0.thumbnail.url}}" type="video/mp4">
                        </video>
                    </div>
                    {% elif review.review_media.all.0 %}
                    <div class="widget_item_review_image">
                        <img data-src='{{review.review_media.all.0.thumbnail.url}}' class="lozad">
                    </div>
                    {% else %}
                    <div class="widget_item_review_image" style="background-color:#f0f0f0">
                        <img src='{{product.list_image}}' style="opacity:0.4">
                    </div>
                    {% endif %}

                    <div class="widget_item_review_text" >{{review.content}}</div>
                </div>
            {% endfor %}
            </div>
        </div>
    </div>
    {% endfor %}
    </div>
</div>


<div class="widget_m">
    <div style="display: flex;flex-wrap: wrap;margin: 0 -2%;">
    {% for product in data_list %}
    <div class="widget_item_container">
        <div class="widget_item">
            <div class="widget_item_product_img" style="background-image:url('{{product.list_image}}')" onclick='redirect_to_product("{{product.product_no}}")'></div>
            {% if widget_option.product_name or widget_option.product_price %}
            <div class="widget_item_product_info" onclick='redirect_to_product("{{product.product_no}}")'>
                {% if widget_option.product_name %}
                <div class="widget_item_product_info_name">{{product.product_name}}</div>
                {% endif %}
                {% if widget_option.product_price %}
                <div class="widget_item_product_info_price">{{product.price}}원</div>
                {% endif %}
            </div>
            {% endif %}

            {% if widget_option.ratings or widget_option.review_num %}
            <div class="widget_item_summary">
                
                {% if widget_option.ratings %}
                
                
                
                <div class="widget_total_ratings_star">
                    <div class="widget_total_ratings_star_empty">
                        <div  class="widget_total_ratings_star_container">
                            {% include 'module/alph_star_empty.html' %}
                        </div>
                    </div>

                    <div class="widget_total_ratings_star_full" style="width: {{product.review_ratings|floatformat:1|rating_width}}%">
                        <div  class="widget_total_ratings_star_container">
                            {% include 'module/alph_star_full.html' %}
                        </div>
                    </div>
                </div>
                <div style="flex-grow:1"></div>

                <div class='widget_item_summary_ratings_1'>평점</div>
                <div class='widget_item_summary_ratings_2'>{{product.review_ratings|floatformat:1}}</div>
                {% endif %}

                {% if widget_option.review_num %}
                <div class='widget_item_summary_num_1'>상품평수 </div>
                <div class='widget_item_summary_num_2'>{{product.review_number|floatformat:"0"}}개</div>
                {% endif %}
            </div>
            {% endif %}
            <div class="widget_item_review_container">

            {% for review in product.review_list  %}
                <div class="widget_item_review" onclick='review_detail_{{widget_id}}({{review.id}},{{product.product_no}})'>
                    {% if review.review_video.all and review.review_video.all.0.thumbnail %}
                    <div class="widget_item_review_image">
                        <video autoplay loop muted playsinline  class="lozad">
                            <source data-src="{{review.review_video.all.0.thumbnail.url}}" type="video/mp4">
                        </video>
                    </div>
                    {% elif review.review_media.all.0 %}
                    <div class="widget_item_review_image">
                        <img data-src='{{review.review_media.all.0.thumbnail.url}}' class="lozad">
                    </div>
                    {% else %}
                    <div class="widget_item_review_image" style="background-color:#f0f0f0">
                        <img src='{{product.list_image}}' style="opacity:0.4">
                    </div>
                    {% endif %}








                    <div class="widget_item_review_text" >{{review.content}}</div>
                </div>
            {% endfor %}
            </div>
        </div>
    </div>
    {% endfor %}
    </div>
</div>

{% if widget_option.pagination %}
<div style="display: flex;width: 100%;">
    <nav style="margin:5px auto;">
      <ul class="pagination">
        <li class="page-item {% if page_current == 1 %}disabled{% endif %}"><a class="page-link" onclick='paging_{{widget_id}}({{page_current|add:'-1'}})'>«</a></li>
        
        {% for i in page_length|pagenation:page_current %}
        <li class="page-item {% if i == page_current %}active{% endif %}"><a class="page-link" onclick='paging_{{widget_id}}({{i}})'>{{i}}</a></li>
        {% endfor %}
        
        <li class="page-item {% if page_current == page_length %}disabled{% endif %}"><a class="page-link" onclick='paging_{{widget_id}}({{page_current|add:'1'}})'>»</a></li>
      </ul>
    </nav>
</div>
{% endif %}

<script>
    observer.observe();
</script>
