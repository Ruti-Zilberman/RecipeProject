from flask_marshmallow import Marshmallow
from models import Recipe, IngredientEntry, User

ma = Marshmallow()

class IngredientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IngredientEntry
        load_instance = True
        include_fk = True

    # כאן הפתרון: אנחנו יוצרים שדה בשם product (קטן) 
    # אבל אומרים לו למשוך נתונים מהעמודה Product (גדול)
    # product = ma.auto_field(column_name="Product")
    # amount = ma.auto_field(column_name="amount")
    # unit = ma.auto_field(column_name="unit")
    # פתרון ההתנגשות: השם ב-JSON יהיה קטן, המקור ב-DB הוא גדול
# אנחנו מסירים את product מרשימת השדות האוטומטיים כדי להגדיר אותו ידנית
        exclude = ("Product",) 

    # כאן הפתרון: אנחנו אומרים לו שהשדה ב-JSON יהיה product (קטן)
    # אבל הוא צריך לקחת את הנתונים מהתכונה Product (גדולה) במודל
    product = ma.Function(lambda obj: obj.Product)  
class RecipeSchema(ma.SQLAlchemyAutoSchema):
    # כאן אנחנו אומרים לסכמה לכלול את רשימת המצרכים בתוך ה-JSON
    ingredients = ma.Nested(IngredientSchema, many=True)
    
    class Meta:
        model = Recipe
        load_instance = True
        # רשימת השדות שיוחזרו לאנגולר (כולל instructions)
        fields = ("id", "name", "description", 
                  "prepTime", "type", "ingredients",
                    "imagePath", "instructions", "rating",
                      "variation_paths", "rating_count", "total_rating_sum")

recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ("password",)

    # אנחנו יוצרים שדות באותיות קטנות כדי שיתאימו ל-TypeScript/HTML שלך
    id = ma.auto_field()
    username = ma.Function(lambda obj: obj.Name) # כאן פתרנו את ה-username שב-HTML
    email = ma.Function(lambda obj: obj.Email)
    role = ma.auto_field()
    is_content_user = ma.auto_field()
    is_approved_uploader = ma.auto_field()
    request_pending = ma.auto_field()

user_schema = UserSchema()
users_schema = UserSchema(many=True)