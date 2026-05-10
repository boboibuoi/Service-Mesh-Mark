import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: Number(__ENV.VUS || 10),
  duration: __ENV.DURATION || "30s",
};

const baseUrl = __ENV.BASE_URL || "http://localhost:8080";

export function setup() {
  if (__ENV.PRODUCT_ID) {
    return { productId: __ENV.PRODUCT_ID };
  }

  const response = http.get(`${baseUrl}/products`);
  if (response.status !== 200) {
    throw new Error(`Cannot load products from ${baseUrl}/products`);
  }

  const products = response.json("products");
  if (!products || products.length === 0) {
    throw new Error("Product list is empty");
  }

  return { productId: products[0].id };
}

export default function (data) {
  const payload = JSON.stringify({
    user_id: __ENV.USER_ID || `load-user-${__VU}-${__ITER}`,
    product_id: data.productId,
    quantity: Number(__ENV.QUANTITY || 1),
    payment_mode: __ENV.PAYMENT_MODE || "success",
  });

  const response = http.post(`${baseUrl}/orders`, payload, {
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": __ENV.IDEMPOTENCY_KEY || `load-${__VU}-${__ITER}-${Date.now()}`,
    },
  });

  check(response, {
    "status is 200": (res) => res.status === 200,
    "order confirmed or payment failed": (res) =>
      res.json("order_status") === "confirmed" ||
      res.json("order_status") === "payment_failed",
  });

  sleep(1);
}
