// *** WARNING: this file was generated by Pulumi SDK Generator. ***
// *** Do not edit by hand unless you're certain you know what you are doing! ***

import * as pulumi from "@pulumi/pulumi";
import * as utilities from "./utilities";

export class SagemakerPredictorLambda extends pulumi.ComponentResource {
    /** @internal */
    public static readonly __pulumiType = 'sagemakerlambda:index:SagemakerPredictorLambda';

    /**
     * Returns true if the given object is an instance of SagemakerPredictorLambda.  This is designed to work even
     * when multiple copies of the Pulumi SDK have been loaded into the same process.
     */
    public static isInstance(obj: any): obj is SagemakerPredictorLambda {
        if (obj === undefined || obj === null) {
            return false;
        }
        return obj['__pulumiType'] === SagemakerPredictorLambda.__pulumiType;
    }

    /**
     * Name of the provisioned SageMaker endpoint.  TODO can we just pass Endpoint type?
     */
    public /*out*/ readonly endpointName!: pulumi.Output<string | undefined>;
    /**
     * Name of the provisioned Lambda function.  TODO can we just return the native object?
     */
    public /*out*/ readonly lambdaFunctionName!: pulumi.Output<string | undefined>;
    /**
     * ARN of the provisioned role that can be reused for model training.
     */
    public /*out*/ readonly trainingRoleArn!: pulumi.Output<string>;

    /**
     * Create a SagemakerPredictorLambda resource with the given unique name, arguments, and options.
     *
     * @param name The _unique_ name of the resource.
     * @param args The arguments to use to populate this resource's properties.
     * @param opts A bag of options that control this resource's behavior.
     */
    constructor(name: string, args: SagemakerPredictorLambdaArgs, opts?: pulumi.ComponentResourceOptions) {
        let inputs: pulumi.Inputs = {};
        opts = opts || {};
        if (!opts.id) {
            if ((!args || args.columnNames === undefined) && !opts.urn) {
                throw new Error("Missing required property 'columnNames'");
            }
            if ((!args || args.modelDataBucket === undefined) && !opts.urn) {
                throw new Error("Missing required property 'modelDataBucket'");
            }
            inputs["accountId"] = args ? args.accountId : undefined;
            inputs["columnNames"] = args ? args.columnNames : undefined;
            inputs["initialInstanceCount"] = args ? args.initialInstanceCount : undefined;
            inputs["instanceType"] = args ? args.instanceType : undefined;
            inputs["modelDataBucket"] = args ? args.modelDataBucket : undefined;
            inputs["modelDataKey"] = args ? args.modelDataKey : undefined;
            inputs["modelFramework"] = args ? args.modelFramework : undefined;
            inputs["modelImage"] = args ? args.modelImage : undefined;
            inputs["region"] = args ? args.region : undefined;
            inputs["endpointName"] = undefined /*out*/;
            inputs["lambdaFunctionName"] = undefined /*out*/;
            inputs["trainingRoleArn"] = undefined /*out*/;
        } else {
            inputs["endpointName"] = undefined /*out*/;
            inputs["lambdaFunctionName"] = undefined /*out*/;
            inputs["trainingRoleArn"] = undefined /*out*/;
        }
        if (!opts.version) {
            opts = pulumi.mergeOptions(opts, { version: utilities.getVersion()});
        }
        super(SagemakerPredictorLambda.__pulumiType, name, inputs, opts, true /*remote*/);
    }
}

/**
 * The set of arguments for constructing a SagemakerPredictorLambda resource.
 */
export interface SagemakerPredictorLambdaArgs {
    /**
     * TODO
     */
    readonly accountId?: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly columnNames: pulumi.Input<pulumi.Input<string>[]>;
    /**
     * TODO
     */
    readonly initialInstanceCount?: pulumi.Input<number>;
    /**
     * TODO
     */
    readonly instanceType?: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly modelDataBucket: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly modelDataKey?: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly modelFramework?: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly modelImage?: pulumi.Input<string>;
    /**
     * TODO
     */
    readonly region?: pulumi.Input<string>;
}