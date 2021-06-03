// *** WARNING: this file was generated by Pulumi SDK Generator. ***
// *** Do not edit by hand unless you're certain you know what you are doing! ***

using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Threading.Tasks;
using Pulumi.Serialization;

namespace Pulumi.Sagemakerlambda
{
    [SagemakerlambdaResourceType("sagemakerlambda:index:SagemakerPredictorLambda")]
    public partial class SagemakerPredictorLambda : Pulumi.ComponentResource
    {
        /// <summary>
        /// Name of the provisioned SageMaker endpoint.  TODO can we just pass Endpoint type?
        /// </summary>
        [Output("endpointName")]
        public Output<string?> EndpointName { get; private set; } = null!;

        /// <summary>
        /// Name of the provisioned Lambda function.  TODO can we just return the native object?
        /// </summary>
        [Output("lambdaFunctionName")]
        public Output<string?> LambdaFunctionName { get; private set; } = null!;

        /// <summary>
        /// ARN of the provisioned role that can be reused for model training.
        /// </summary>
        [Output("trainingRoleArn")]
        public Output<string> TrainingRoleArn { get; private set; } = null!;


        /// <summary>
        /// Create a SagemakerPredictorLambda resource with the given unique name, arguments, and options.
        /// </summary>
        ///
        /// <param name="name">The unique name of the resource</param>
        /// <param name="args">The arguments used to populate this resource's properties</param>
        /// <param name="options">A bag of options that control this resource's behavior</param>
        public SagemakerPredictorLambda(string name, SagemakerPredictorLambdaArgs args, ComponentResourceOptions? options = null)
            : base("sagemakerlambda:index:SagemakerPredictorLambda", name, args ?? new SagemakerPredictorLambdaArgs(), MakeResourceOptions(options, ""), remote: true)
        {
        }

        private static ComponentResourceOptions MakeResourceOptions(ComponentResourceOptions? options, Input<string>? id)
        {
            var defaultOptions = new ComponentResourceOptions
            {
                Version = Utilities.Version,
            };
            var merged = ComponentResourceOptions.Merge(defaultOptions, options);
            // Override the ID if one was specified for consistency with other language SDKs.
            merged.Id = id ?? merged.Id;
            return merged;
        }
    }

    public sealed class SagemakerPredictorLambdaArgs : Pulumi.ResourceArgs
    {
        /// <summary>
        /// TODO
        /// </summary>
        [Input("accountId")]
        public Input<string>? AccountId { get; set; }

        [Input("columnNames", required: true)]
        private InputList<string>? _columnNames;

        /// <summary>
        /// TODO
        /// </summary>
        public InputList<string> ColumnNames
        {
            get => _columnNames ?? (_columnNames = new InputList<string>());
            set => _columnNames = value;
        }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("initialInstanceCount")]
        public Input<int>? InitialInstanceCount { get; set; }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("instanceType")]
        public Input<string>? InstanceType { get; set; }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("modelDataBucket", required: true)]
        public Input<string> ModelDataBucket { get; set; } = null!;

        /// <summary>
        /// TODO
        /// </summary>
        [Input("modelDataKey")]
        public Input<string>? ModelDataKey { get; set; }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("modelFramework")]
        public Input<string>? ModelFramework { get; set; }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("modelImage")]
        public Input<string>? ModelImage { get; set; }

        /// <summary>
        /// TODO
        /// </summary>
        [Input("region")]
        public Input<string>? Region { get; set; }

        public SagemakerPredictorLambdaArgs()
        {
        }
    }
}