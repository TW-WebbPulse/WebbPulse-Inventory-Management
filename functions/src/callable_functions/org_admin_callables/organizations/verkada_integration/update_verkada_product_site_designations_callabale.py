from firebase_functions import https_fn
from src.shared import db, apply_rate_limiting, POSTcorsrules, logger
from src.helper_functions.auth.auth_functions import (
    check_user_is_org_admin,
    check_user_is_authed,
    check_user_token_current,
    check_user_is_email_verified,
)


@https_fn.on_call(cors=POSTcorsrules)
def update_verkada_product_site_designations_callable(
    req: https_fn.CallableRequest,
) -> any:
    # Apply rate limiting
    apply_rate_limiting(req, "update_verkada_product_site_designations_callable")

    org_id = req.data.get("orgId")
    product_site_designations = req.data.get("productSiteDesignations")

    check_user_is_authed(req)
    check_user_is_org_admin(req, org_id)
    check_user_token_current(req)
    check_user_is_email_verified(req)

    if (
        org_id is None
        or product_site_designations is None
        or not isinstance(product_site_designations, dict)
    ):
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.INVALID_ARGUMENT,
            message="The function must be called with orgId and a valid productSiteDesignations map.",
        )

    try:
        org_ref = db.collection("organizations").document(org_id)
        org_ref.update({"orgVerkadaProductSiteDesignations": product_site_designations})
        return {"response": "Verkada product site designations updated successfully."}
    except Exception as e:
        logger.error(
            f"Error updating Verkada product site designations: {str(e)}", exc_info=True
        )
        raise https_fn.HttpsError(
            code=https_fn.FunctionsErrorCode.UNKNOWN,
            message=f"An error occurred: {str(e)}",
        )
