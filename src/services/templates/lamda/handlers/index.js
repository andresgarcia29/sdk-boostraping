exports.handler = async (event) => {
  let responseBody = {
    message: "Hello from Lambda!",
    input: event,
  };

  const response = {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(responseBody),
  };

  return response;
};
