import * as sl from "@pulumi/sagemakerlambda";

const page = new sl.StaticPage("page", {
    indexContent: "<html><body><p>Hello world!</p></body></html>",
});

export const bucket = page.bucket;
export const url = page.websiteUrl;
