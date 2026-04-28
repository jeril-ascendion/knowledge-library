/**
 * Ascendion Engineering — CloudFront viewer-request function
 *
 * Rewrites directory-style URLs to their underlying index.html so
 * static-site URLs like /knowledge-graph/ and /principles/cloud-native/
 * resolve correctly against the S3 origin.
 *
 * Without this function:
 *   /knowledge-graph/      → S3 looks for object "knowledge-graph/" → 403
 *   /principles/foundational/ → S3 looks for object "principles/foundational/" → 403
 *
 * With this function:
 *   /knowledge-graph/      → request rewritten to /knowledge-graph/index.html
 *   /principles/foundational/ → request rewritten to /principles/foundational/index.html
 *   /shared.css            → passed through unchanged (has extension)
 *   /                      → passed through (CloudFront handles via default root object)
 *
 * Deployed manually via AWS Console → CloudFront → Functions, then
 * associated with the distribution's default behavior on viewer-request.
 * Runtime: cloudfront-js-2.0
 */
function handler(event) {
    var request = event.request;
    var uri = request.uri;

    // Skip if the URI already targets a specific file (has an extension)
    if (uri.match(/\.[a-zA-Z0-9]+$/)) {
        return request;
    }

    // Directory-style URL ending with "/" — append index.html
    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
        return request;
    }

    // Path without trailing slash and no extension — treat as directory
    request.uri = uri + '/index.html';
    return request;
}
