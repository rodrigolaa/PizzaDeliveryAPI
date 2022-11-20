from fastapi import APIRouter, Depends,status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User,Order
from schemas import OrderModel,OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder



order_router =APIRouter(
    prefix='/orders',
    tags = ['orders']
)


session = Session(bind=engine)

@order_router.get("/")

async def hello(Authorize:AuthJWT=Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Invalid Token"
        )

    return{"message": "Hello World"}


@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel,Authorize:AuthJWT=Depends()):

    """
        ## Placing an Order
        This Router needs the followig
        - quantity: integer
        - pizza size: string
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user=Authorize.get_jwt_subject()

    user=session.query(User).filter(User.username==current_user).first()

    new_order=Order(
        pizza_size=order.pizza_size,
        quantity = order.quantity,

    )

    new_order.user=user

    session.add(new_order)

    session.commit()


    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status":new_order.order_status
    }


    return jsonable_encoder(response)

#GET ALL ORDERS FROM DB ONLY FOR STAFF USERS
@order_router.get('/orders')

async def list_all_orders(Authorize:AuthJWT=Depends()):

    """
        ## Lists all orders
        This Router needs the staff permission
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )



    current_user=Authorize.get_jwt_subject()

    user=session.query(User).filter(User.username==current_user).first()

    if user.is_staff:

        orders=session.query(Order).all()

        return jsonable_encoder(orders)
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not superuser"
        )

#GET ORDERS FROM A ORDER ID ONLY A SUPER USE CAN SEARCH FOR ANY SPECIFIC ORDER
@order_router.get('/orders/{id}')

async def get_order_id(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Get an order by its ID
        This Router retrieve an order information by its ID. Needs Staff permission.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )



    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()

    if current_user.is_staff:

        order=session.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not superuser"
        )

#GET ORDERS FROM A USER ID LOGGED IN
@order_router.get('/user/orders')

async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get all orders associated with an user.
        This Router retrieve all orders information by the user logged in.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders)


#GET SPECIFC ORDER FROM A USER ID LOGGED IN    
@order_router.get('/user/orders/{id}')

async def get_specific_order(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Get a specifc order associated with the user logged in.
        This Router retrieve an order information by the user logged in.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()

    orders=current_user.orders

    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)

    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID not found"
        )

#UPDATE SPECIFC ORDER FROM A USER ID LOGGED IN    
@order_router.put('/order/update/{id}')

async def update_specific_order(id:int,order:OrderModel,Authorize:AuthJWT=Depends()):
    """
        ## Update a specifc order associated with the user logged in.
        This Router update an order information by the user logged in. Requires the following fields
        - quantity: integer
        - pizza size: string
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    user=Authorize.get_jwt_subject()

    order_to_update=session.query(Order).filter(Order.id==id).first()
    
    order_to_update.quantity=order.quantity

    order_to_update.pizza_size=order.pizza_size

    session.commit()

    response = {
                "id": order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,

            }

    return jsonable_encoder(response)


#UPDATE STATUS ORDER  
@order_router.patch('/order/status/{id}')

async def update_order_status(id:int,order:OrderStatusModel,Authorize:AuthJWT=Depends()):
    """
        ## Update a specifc order status. Requires Staff permission.
        This Router update an order status. Requires the following fields
        - order_status: string
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    
    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()

    if current_user.is_staff:

        order_to_update=session.query(Order).filter(Order.id==id).first()

        order_to_update.order_status = order.order_status

        session.commit()
        
        response = {
                "id": order_to_update.id,
                "quantity":order_to_update.quantity,
                "pizza_size":order_to_update.pizza_size,
                "order_status":order_to_update.order_status,

            }

        return jsonable_encoder(response)
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not superuser"
        )

#DELETE AN ORDER  
@order_router.delete('/order/delete/{id}',status_code=status.HTTP_204_NO_CONTENT)

async def update_order_status(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Delete a specifc order status. 
        This Router delete an order associated to its user. Or, in case of staff member, delete any order.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    user=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==user).first()


    try:
        if current_user.is_staff:
            order_to_delete=session.query(Order).filter(Order.id==id).first()
            session.delete(order_to_delete)
            session.commit()
        else:
            order_to_delete=session.query(Order).filter(User.username==user).filter(Order.id==id).first()
            session.delete(order_to_delete)
            session.commit()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order ID not Found"
        )
    # session.delete(order_to_delete)

    # session.commit()

    return order_to_delete
    
