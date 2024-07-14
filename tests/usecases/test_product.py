from typing import List
from uuid import UUID

import pytest
from store.core.exceptions import NotFoundException, DuplicateEntryException
from store.schemas.product import ProductOut, ProductUpdateOut
from store.usecases.product import ProductUsecase


async def test_usecases_create_should_return_success(product_in):
    result = await ProductUsecase().create(body=product_in)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"

async def test_usecases_create_should_raise_duplicate_entry_exception(product_in):
    # Create a product
    await ProductUsecase().create(body=product_in)

    # Test DuplicateEntryException
    with pytest.raises(DuplicateEntryException):
        await ProductUsecase().create(body=product_in)

    # Verify message
    assert err.value.message == "An entry with the same key(s) already exists"

async def test_usecases_get_should_return_success(product_inserted):
    result = await ProductUsecase().get(id=product_inserted.id)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecases_get_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await ProductUsecase().get(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert (
        err.value.message
        == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
    )


@pytest.mark.usefixtures("products_inserted")
async def test_usecases_query_should_return_success():
    result = await ProductUsecase().query()

    assert isinstance(result, List)
    assert len(result) > 1


async def test_usecases_update_should_return_success(product_up, product_inserted):
    product_up.price = "7.500"
    result = await ProductUsecase().update(id=product_inserted.id, body=product_up)

    assert isinstance(result, ProductUpdateOut)


async def test_usecases_update_should_not_found(product_up):
    with pytest.raises(NotFoundException) as err:
        await ProductUsecase().update(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"), body=product_up)

    assert (
        err.value.message == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
    )

async def test_usecases_delete_should_return_success(product_inserted):
    result = await ProductUsecase().delete(id=product_inserted.id)

    assert result is True


async def test_usecases_delete_should_not_found():
    with pytest.raises(NotFoundException) as err:
        await ProductUsecase().delete(id=UUID("1e4f214e-85f7-461a-89d0-a751a32e3bb9"))

    assert (
        err.value.message
        == "Product not found with filter: 1e4f214e-85f7-461a-89d0-a751a32e3bb9"
    )

