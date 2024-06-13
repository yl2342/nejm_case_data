# Copyright 2024 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.

import argparse
import logging
import os.path
import json
import sys
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

def handle_exception(exception_type, exception_message, status_code):
    logging.info(exception_type)
    if status_code is not None:
        logging.info(status_code)
    logging.info(exception_message)

def main():

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Extract text from a PDF file using Adobe API and save it as a zip file to the specified location.')
    parser.add_argument('input_pdf', type=str, help='path to the input PDF file.')
    parser.add_argument('output_zip', type=str, help='path where the output zip file will be saved.')
    args = parser.parse_args()

    try:
        # Initial setup, create credentials instance.

        # load client_id and client_secret from the pdfservices-api-credentials.json file
        # read the json file
        with open('pdfservices-api-credentials.json') as f:
            # load the json file
            credentials = json.load(f)
            # get the client_id and client_secret
            client_id = credentials['client_credentials']['client_id']
            client_secret = credentials['client_credentials']['client_secret']

        # Create credentials instance using client_id and client_secret.
        credentials = Credentials.service_principal_credentials_builder(). \
            with_client_id(client_id). \
            with_client_secret(client_secret). \
            build()

        # Create an ExecutionContext using credentials and create a new operation instance.
        execution_context = ExecutionContext.create(credentials)
        extract_pdf_operation = ExtractPDFOperation.create_new()

        # Set operation input from a source file.
        source = FileRef.create_from_local_file(args.input_pdf)
        extract_pdf_operation.set_input(source)

        # Build ExtractPDF options and set them into the operation
        extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
            .with_element_to_extract(ExtractElementType.TEXT) \
            .build()
        extract_pdf_operation.set_options(extract_pdf_options)

        # Execute the operation.
        result: FileRef = extract_pdf_operation.execute(execution_context)

        # Save the result to the specified location.
        result.save_as(args.output_zip)


    except ServiceApiException as service_api_exception:
        # ServiceApiException is thrown when an underlying service API call results in an error.
        handle_exception("ServiceApiException", service_api_exception.message, service_api_exception.status_code)
    except ServiceUsageException as service_usage_exception:
        # ServiceUsageException is thrown when either service usage limit has been reached or credentials quota has been
        # exhausted.
        handle_exception("ServiceUsageException", service_usage_exception.message, service_usage_exception.status_code)
    except SdkException as sdk_exception:
        # SdkException is typically thrown for client-side or network errors.
        handle_exception("SdkException", sdk_exception.message, None)



if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Extract text from a PDF file. Convert the PDF file to a zip file containing the extracted text.')
    # parser.add_argument('input_pdf', type=str, help='PDF file name')
    # args = parser.parse_args()
    main()