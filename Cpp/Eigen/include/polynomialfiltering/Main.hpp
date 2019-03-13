/***** /PolynomialFiltering/Main/
 * (C) Copyright 2019 - Blue Lightning Development, LLC.
 * D. F. Linton. support@BlueLightningDevelopment.com
 *
 * SPDX-License-Identifier: MIT
 * See separate LICENSE file for full text
 *
 * AUTO-GENERATED C++
 */
#ifndef ___POLYNOMIALFILTERING_MAIN_HPP
#define ___POLYNOMIALFILTERING_MAIN_HPP

#include <math.h>

#include <polynomialfiltering/PolynomialFilteringEigen.hpp>



namespace PolynomialFiltering {
    enum FilterStatus {
        IDLE = 0,
        INITIALIZING = 1,
        RUNNING = 2,
        COASTING = 3,
        RESETING = 4,
    }; // class FilterStatus 

    class AbstractFilter {
        public:
            AbstractFilter(const std::string name="");
            static RealMatrix stateTransitionMatrix(const long N, const double dt);
            std::string getName();
            void setName(const std::string name);
            FilterStatus getStatus();
            void setStatus(const FilterStatus status);
            virtual long getN() = 0;
            virtual double getTime() = 0;
            virtual RealVector getState(const double t) = 0;
        protected:
            std::string name;
            FilterStatus status;
    }; // class AbstractFilter 

    class ManagedFilterBase : public AbstractFilter {
        public:
            ManagedFilterBase();
            virtual double getGoodnessOfFit() = 0;
            virtual double getBiasOfFit() = 0;
            virtual void add(const double t, const RealVector& y, const std::string observationId="") = 0;
            void addWithVariance(const double t, const RealVector& y, const RealMatrix& R, const std::string observationId="");
    }; // class ManagedFilterBase 

}; // namespace PolynomialFiltering


#endif // ___POLYNOMIALFILTERING_MAIN_HPP