from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from api.client import (
    APIError,
    ai_search,
    get_properties,
    get_property,
    get_property_images,
    search_properties,
    semantic_search,
    hybrid_search,
    register_user,
    login_user,
    get_current_user,
)

app = Flask(__name__)

app.secret_key = "QBAC1RBAC"


@app.context_processor
def inject_globals():
    return {
        "app_name": "Property Dealer AI",
    }


@app.route("/")
def home():
    error = None
    properties = []

    try:
        properties = get_properties()
    except APIError as exc:
        error = str(exc)

    return render_template(
        "index.html",
        properties=properties[:6],
        error=error,
    )


@app.route("/properties")
def properties():
    error = None
    result = None

    filters = {
        "location": request.args.get("location", "").strip(),
        "property_type": request.args.get(
            "property_type",
            "",
        ).strip(),
        "listing_type": request.args.get(
            "listing_type",
            "",
        ).strip(),
        "min_price": request.args.get(
            "min_price",
            "",
        ).strip(),
        "max_price": request.args.get(
            "max_price",
            "",
        ).strip(),
        "bedrooms": request.args.get(
            "bedrooms",
            "",
        ).strip(),
    }

    has_filters = any(filters.values())

    try:
        if has_filters:
            result = search_properties(
                location=filters["location"] or None,
                property_type=(
                    filters["property_type"] or None
                ),
                listing_type=(
                    filters["listing_type"] or None
                ),
                min_price=_to_float(
                    filters["min_price"]
                ),
                max_price=_to_float(
                    filters["max_price"]
                ),
                bedrooms=_to_int(
                    filters["bedrooms"]
                ),
            )
        else:
            items = get_properties()
            
            result = {
                "items": items,
                "total": len(items),
                "page": 1,
                "limit": 10,
                "total_pages": 1,
            }

    except APIError as exc:
        error = str(exc)
        result = {
            "items": [],
            "total": 0,
            "page": 1,
            "limit": 10,
            "total_pages": 0,
        }

    return render_template(
        "properties.html",
        result=result,
        filters=filters,
        error=error,
    )


@app.route("/properties/<int:property_id>")
def property_detail(property_id: int):
    error = None
    property_data = None
    images = []

    try:
        property_data = get_property(property_id)
        images = get_property_images(property_id)
    except APIError as exc:
        error = str(exc)

    return render_template(
        "property_detail.html",
        property=property_data,
        images=images,
        error=error,
    )


@app.route("/search")
def search():
    error = None
    result = None

    query = request.args.get(
        "query",
        "",
    ).strip()

    filters = {
        "location": request.args.get(
            "location",
            "",
        ).strip(),
        "property_type": request.args.get(
            "property_type",
            "",
        ).strip(),
        "listing_type": request.args.get(
            "listing_type",
            "",
        ).strip(),
        "min_price": request.args.get(
            "min_price",
            "",
        ).strip(),
        "max_price": request.args.get(
            "max_price",
            "",
        ).strip(),
        "bedrooms": request.args.get(
            "bedrooms",
            "",
        ).strip(),
    }

    if query or any(filters.values()):
        try:
            result = search_properties(
                location=filters["location"] or None,
                property_type=(
                    filters["property_type"] or None
                ),
                listing_type=(
                    filters["listing_type"] or None
                ),
                min_price=_to_float(
                    filters["min_price"]
                ),
                max_price=_to_float(
                    filters["max_price"]
                ),
                bedrooms=_to_int(
                    filters["bedrooms"]
                ),
            )
        except APIError as exc:
            error = str(exc)

    return render_template(
        "search.html",
        result=result,
        query=query,
        filters=filters,
        error=error,
    )


@app.route("/semantic-search")
def semantic_search_page():
    error = None
    results = []
    query = request.args.get(
        "query",
        "",
    ).strip()

    if query:
        try:
            results = semantic_search(query)
        except APIError as exc:
            error = str(exc)

    return render_template(
        "properties.html",
        result={
            "items": [
                item["property"]
                for item in results
            ],
            "total": len(results),
            "page": 1,
            "limit": len(results),
            "total_pages": 1,
        },
        filters={},
        error=error,
        search_mode="Semantic Search",
    )


@app.route("/hybrid-search")
def hybrid_search_page():
    error = None
    results = []

    query = request.args.get(
        "query",
        "",
    ).strip()

    if query:
        try:
            data = hybrid_search(query)

            if isinstance(data, dict):
                results = [
                    item["property"]
                    for item in data.get("items", [])
                ]
            else:
                results = [
                    item["property"]
                    for item in data
                ]

        except APIError as exc:
            error = str(exc)

    return render_template(
        "properties.html",
        result={
            "items": results,
            "total": len(results),
            "page": 1,
            "limit": len(results),
            "total_pages": 1,
        },
        filters={},
        error=error,
        search_mode="Hybrid Search",
    )


@app.route("/ai-search")
def ai_search_page():
    error = None
    result = None

    query = request.args.get(
        "query",
        "",
    ).strip()

    if query:
        try:
            result = ai_search(query)
        except APIError as exc:
            error = str(exc)

    return render_template(
        "ai_search.html",
        result=result,
        query=query,
        error=error,
    )


def _to_float(value: str):
    if not value:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def _to_int(value: str):
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        return None
    
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            error = "All fields are required."

        else:
            try:
                register_user(
                    name=name,
                    email=email,
                    password=password,
                )

                return redirect(
                    url_for("login")
                )

            except APIError as exc:
                error = str(exc)

    return render_template(
        "signup.html",
        error=error,
    )
    
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Email and password are required."

        else:
            try:
                token_data = login_user(
                    email=email,
                    password=password,
                )

                session["access_token"] = token_data[
                    "access_token"
                ]

                return redirect(
                    url_for("profile")
                )

            except APIError as exc:
                error = str(exc)

    return render_template(
        "login.html",
        error=error,
    )
    
@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("home")
    )
    
@app.route("/profile")
def profile():
    token = session.get("access_token")

    if not token:
        return redirect(
            url_for("login")
        )

    try:
        user = get_current_user(token)

    except APIError:
        session.clear()

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        user=user,
    )
    
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
