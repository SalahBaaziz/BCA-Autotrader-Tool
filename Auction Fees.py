def calculate_fixed_auction_fee(cap_price, interval_ranges, auction_fee_list):
    """
    Finds the correct interval for cap_price and returns the corresponding fixed auction_fee.
    """
    for i, (low, high) in enumerate(interval_ranges):
        if low <= cap_price <= high:
            return auction_fee_list[i]
    return None  # Return None if no interval is found (cap_price is too high or invalid)


def calculate_cap_price_from_max_price(max_price, assurance_fee, interval_ranges, auction_fee_list, v5_fee, advertising_fee=50, transport_fee=80):
    """
    Calculates the cap price given a maximum price by deducting the auction fee and assurance fee.
    """
    for cap_price in range(max_price, 0, -1):  # Iterate backward from max_price to 0
        auction_fee = calculate_fixed_auction_fee(cap_price, interval_ranges, auction_fee_list)
        if auction_fee is not None:
            total_price = cap_price + auction_fee + assurance_fee + v5_fee + advertising_fee + transport_fee
            if total_price <= max_price:
                return cap_price
    return None  # Return None if no valid cap price is found


# Define interval ranges and auction fee list
interval_ranges = [
    (11, 49), (50, 99), (100, 149), (150, 199), (200, 249), (250, 299),
    (300, 349), (350, 399), (400, 449), (450, 499), (500, 749), (750, 999),
    (1000, 1249), (1250, 1499), (1500, 1749), (1750, 1999), (2000, 2249),
    (2250, 2499), (2500, 2749), (2750, 2999), (3000, 3249), (3250, 3499),
    (3500, 3749), (3750, 3999), (4000, 4249), (4250, 4499), (4500, 4749),
    (4750, 4999), (5000, 5249), (5250, 5499), (5500, 5749), (5750, 5999),
    (6000, 6249), (6250, 6499), (6500, 6749), (6750, 6999), (7000, 7249),
    (7250, 7499), (7500, 7749), (7750, 7999), (8000, 8249), (8250, 8499),
    (8500, 8749), (8750, 8999), (9000, 9249), (9250, 9499), (9500, 9749),
    (9750, 9999), (10000, 10249), (10250, 10499), (10500, 10749),
    (10750, 10999), (11000, 11249), (11250, 11499), (11500, 1000000)
]

auction_fee_list = [
    49.84, 83.85, 123.00, 169.39, 182.99, 190.84, 243.01, 249.22, 263.16, 269.57,
    307.21, 325.23, 345.51, 359.11, 373.25, 393.68, 413.14, 418.07, 422.36, 422.64,
    480.48, 485.25, 494.20, 497.24, 501.67, 503.81, 508.21, 512.36, 520.22, 525.00,
    529.83, 536.08, 536.26, 539.44, 546.80, 553.20, 553.19, 558.81, 569.34, 580.50,
    584.67, 590.43, 590.97, 591.92, 600.54, 605.38, 607.52, 620.72, 645.84, 660.03,
    662.42, 679.61, 695.34, 709.29, 1435.00
]
# Menu for user to choose an operation
def main():
    print("Choose an operation:")
    print("1. Calculate Total Price")
    print("2. Calculate Cap Price")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        cap_price = int(input("Enter the cap price: "))
        assurance_fee = 66.80
        advertising_fee = 50
        transport_fee = 50
        v5_fee = 0
        auction_fee = calculate_fixed_auction_fee(cap_price, interval_ranges, auction_fee_list)
        if auction_fee is not None:
            total_price = cap_price + auction_fee + assurance_fee + v5_fee + advertising_fee + transport_fee
            print(f"Total Price: {total_price}")
        else:
            print("Cap price is out of range.")
    elif choice == "2":
        max_price = int(input("Enter the maximum price: "))
        assurance_fee = 66.80
        advertising_fee = 50
        transport_fee = 0
        v5_fee = 0
        calculated_cap_price = calculate_cap_price_from_max_price(max_price, assurance_fee, interval_ranges, auction_fee_list, v5_fee, advertising_fee, transport_fee)
        if calculated_cap_price is not None:
            print(f"Calculated Cap Price: {calculated_cap_price}")
        else:
            print("No valid cap price found for the given max price.")
    else:
        print("Invalid choice. Please enter 1 or 2.")

# Run the program
if __name__ == "__main__":
    main()