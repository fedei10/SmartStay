import { PRODUCTS } from './products';

export async function getProductPrice(productId: string) {
  return PRODUCTS.find((product) => product.id === productId)?.priceInCents ?? null;
}
